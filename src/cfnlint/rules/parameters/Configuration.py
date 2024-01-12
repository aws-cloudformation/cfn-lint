"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from typing import Any

from cfnlint.data.schemas.other import parameters as schema_parameters
from cfnlint.helpers import load_resource
from cfnlint.jsonschema import Validator
from cfnlint.jsonschema._validators_cfn import cfn_type
from cfnlint.rules.jsonschema.Base import BaseJsonSchema


class Configuration(BaseJsonSchema):
    """Check if Parameters are configured correctly"""

    id = "E2001"
    shortdesc = "Parameters have appropriate properties"
    description = "Making sure the parameters are properly configured"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/parameters-section-structure.html"
    tags = ["parameters"]

    def __init__(self):
        """Init"""
        super().__init__()
        self.rule_set = {
            "additionalProperties": "E2001",
            "patternProperties": "E2001",
            "properties": "E2001",
            "propertyNames": "E2003",
            "maxProperties": "E2010",
            "minProperties": "E2010",
            "required": "E2001",
            "type": "E2001",
            "enum": "E2002",
            "maxLength": "E2012",
            "maximum": "E2012",
        }
        self.validators["type"] = cfn_type
        self.child_rules = dict.fromkeys(list(self.rule_set.values()))
        self.schema = load_resource(schema_parameters, "configuration.json")

    # pylint: disable=unused-argument
    def cfnparameters(self, validator: Validator, _, instance: Any, schema):
        validator = self.extend_validator(validator, self.schema, validator.context)
        for err in validator.iter_errors(instance):
            if err.rule is None:
                if err.validator in self.rule_set:
                    err.rule = self.child_rules[self.rule_set[err.validator]]
                elif not err.validator.startswith("fn") and err.validator != "ref":
                    err.rule = self
            yield err
