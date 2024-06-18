"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import logging
from typing import Any, Sequence

from cfnlint.context import Context
from cfnlint.jsonschema import V, ValidationError, Validator
from cfnlint.rules import CloudFormationLintRule, RuleMatch
from cfnlint.schema.resolver import RefResolver

LOGGER = logging.getLogger("cfnlint.rules.jsonschema")


class BaseJsonSchema(CloudFormationLintRule):
    """The base JSON schema package"""

    def __init__(self) -> None:
        """Init"""
        super().__init__()
        self.rules: dict[str, Any] = {}
        self.rule_set: dict[str, str] = {}
        self.validators: dict[str, V] = {}

    def _convert_validation_errors_to_matches(
        self,
        path: Sequence[str],
        e: ValidationError,
    ):
        matches = []
        kwargs: dict[Any, Any] = {}
        if e.extra_args:
            kwargs = e.extra_args
        e_path = list(path) + list(e.path)
        if len(e.path) > 0:
            e_path_override = e.path_override
            if e_path_override:
                e_path = list(e_path_override)
            else:
                key = e.path[-1]
                if hasattr(key, "start_mark"):
                    kwargs["location"] = (
                        key.start_mark.line,
                        key.start_mark.column,
                        key.end_mark.line,
                        key.end_mark.column,
                    )
        e_rule = None
        if e.rule:
            e_rule = e.rule
        if not e_rule:
            rs_rule = self.child_rules.get(self.rule_set.get(e.validator, ""), self)
            # if the value is None it means the rule was disabled
            # so we continue
            if rs_rule is None:
                return []

            e_rule = rs_rule

        match = RuleMatch(
            e_path,
            e.message,
            rule=e_rule,
            context=[],
            **kwargs,
        )

        matches.append(match)

        if e.context:
            for err in e.context:
                match.context.extend(
                    self._convert_validation_errors_to_matches(path, err)
                )

        return matches

    def json_schema_validate(
        self, validator: Validator, properties: dict[str, Any], path: Sequence[str]
    ):
        matches = []
        for err in validator.iter_errors(properties):
            matches.extend(self._convert_validation_errors_to_matches(path, err))

        return matches

    @property
    def schema(self) -> Any:
        return {}

    def _clean_error(self, err: ValidationError):
        if err.rule is None:
            if err.validator:
                if err.validator in self.rule_set:
                    err.rule = self.child_rules[self.rule_set[err.validator]]
                elif not err.validator.startswith("fn") and err.validator != "ref":
                    err.rule = self
            else:
                err.rule = self
        for i, c in enumerate(err.context):
            err.context[i] = self._clean_error(c)
        return err

    def _validate(self, validator: Validator, instance: Any):
        for err in validator.iter_errors(instance):
            yield self._clean_error(err)

    # pylint: disable=unused-argument
    def validate(self, validator: Validator, _, instance: Any, schema):
        validator = self.extend_validator(
            validator, self.schema, validator.context.evolve()
        )
        yield from self._validate(validator, instance)

    def _get_validators(self) -> dict[str, V]:
        validators = self.validators.copy()
        for name, rule_id in self.rule_set.items():
            rule = self.child_rules.get(rule_id)
            if rule is not None:
                if hasattr(rule, name) and callable(getattr(rule, name)):
                    validators[name] = getattr(rule, name)

        return validators

    def extend_validator(
        self, validator: Validator, schema: Any, context: Context
    ) -> Validator:
        return validator.extend(validators=self._get_validators())(
            schema=schema
        ).evolve(
            cfn=validator.cfn,
            context=context,
            resolver=RefResolver.from_schema(
                schema,
            ),
        )
