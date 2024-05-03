"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import logging
import random
import string
from typing import Any, Dict, List

from cfnlint.context import Context
from cfnlint.jsonschema import V, ValidationError, Validator
from cfnlint.rules import CloudFormationLintRule, RuleMatch

LOGGER = logging.getLogger("cfnlint.rules.jsonschema")


class BaseJsonSchema(CloudFormationLintRule):
    """The base JSON schema package"""

    def __init__(self) -> None:
        """Init"""
        super().__init__()
        self.rules: Dict[str, Any] = {}
        self.rule_set: Dict[str, str] = {}
        self.validators: Dict[str, V] = {}

    def _convert_validation_errors_to_matches(
        self, path: List[str], e: ValidationError
    ):
        matches = []
        kwargs: Dict[Any, Any] = {}
        if e.extra_args:
            kwargs = e.extra_args
        e_path = path + list(e.path)
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
            rs_rule = self.child_rules.get(self.rule_set.get(e.validator), self)
            # if the value is None it means the rule was disabled
            # so we continue
            if rs_rule is None:
                return []

            e_rule = rs_rule

        if e.context:

            parent_id = "".join(
                random.choices(string.ascii_lowercase + string.digits, k=5)  # nosec
            )
            e.message = f"{e.message} (id {parent_id!r})"
            for err in e.context:
                err.path.extend(e.path)
                err.message = (
                    f"{err.message} (parent {parent_id!r}. "
                    "Schema group {err.schema_path[0]!r})"
                )
                matches.extend(self._convert_validation_errors_to_matches(path, err))

        matches.append(
            RuleMatch(
                e_path,
                e.message,
                rule=e_rule,
                **kwargs,
            )
        )
        return matches

    def json_schema_validate(self, validator, properties, path):
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

    def _get_validators(self) -> Dict[str, V]:
        validators = self.validators.copy()
        for name, rule_id in self.rule_set.items():
            rule = self.child_rules.get(rule_id)
            if rule is not None:
                if hasattr(rule, name) and callable(getattr(rule, name)):
                    validators[name] = getattr(rule, name)

        return validators

    # ToDo Do we really need this?
    def extend_validator(
        self, validator: Validator, schema: Any, context: Context
    ) -> Validator:
        return validator.extend(validators=self._get_validators())(
            schema=schema
        ).evolve(cfn=validator.cfn, context=context)
