"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from typing import Any

from cfnlint.data.schemas.other import conditions as schema_conditions
from cfnlint.helpers import FUNCTION_CONDITIONS, load_resource
from cfnlint.jsonschema import Validator
from cfnlint.jsonschema._validators_cfn import cfn_type
from cfnlint.rules.jsonschema.Base import BaseJsonSchema


class Configuration(BaseJsonSchema):
    """Check if Conditions are configured correctly"""

    id = "E8001"
    shortdesc = "Conditions have appropriate properties"
    description = "Check if Conditions are properly configured"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/conditions-section-structure.html"
    tags = ["conditions"]

    def __init__(self):
        """Init"""
        super().__init__()
        self.rule_set = {
            "fn_equals": "E8003",
            "fn_not": "E8005",
            "fn_and": "E8004",
            "fn_or": "E8006",
            "condition": "E8007",
        }
        self.child_rules = dict.fromkeys(list(self.rule_set.values()))
        self.schema = load_resource(schema_conditions, "conditions.json")

    # pylint: disable=unused-argument
    def cfnconditions(self, validator: Validator, _, instance: Any, schema):
        validator = validator.evolve(
            context=validator.context.evolve(
                functions=FUNCTION_CONDITIONS + ["Ref", "Condition"],
                resources={},
            ),
        )
        validator = self.extend_validator(validator, self.schema, validator.context)
        validator = validator.extend(
            validators={
                "type": cfn_type,
            }
        )(self.schema)

        for err in validator.iter_errors(instance):
            if err.rule is None:
                if err.validator in self.rule_set:
                    err.rule = self.child_rules[self.rule_set[err.validator]]
                elif not err.validator.startswith("fn") and err.validator != "ref":
                    err.rule = self
            yield err
