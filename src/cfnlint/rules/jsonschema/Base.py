"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import logging
from typing import Any, Dict

from cfnlint.context import Context
from cfnlint.jsonschema import Validator
from cfnlint.jsonschema._typing import V
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

    def json_schema_validate(self, validator, properties, path):
        matches = []
        for e in validator.iter_errors(properties):
            kwargs = {}
            if e.extra_args:
                kwargs = e.extra_args
            e_path = path + list(e.path)
            if len(e.path) > 0:
                e_path_override = getattr(e, "path_override", None)
                if e_path_override:
                    e_path = list(e.path_override)
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
                    continue

                e_rule = rs_rule

            matches.append(
                RuleMatch(
                    e_path,
                    e.message,
                    rule=e_rule,
                    **kwargs,
                )
            )

        return matches

    @property
    def schema(self) -> Any:
        return {}

    # pylint: disable=unused-argument
    def validate(self, validator: Validator, _, instance: Any, schema):
        validator = self.extend_validator(validator, self.schema, validator.context)
        for err in validator.iter_errors(instance):
            if err.rule is None:
                if err.validator in self.rule_set:
                    err.rule = self.child_rules[self.rule_set[err.validator]]
                elif not err.validator.startswith("fn") and err.validator != "ref":
                    err.rule = self
            yield err

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
