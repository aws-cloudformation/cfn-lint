"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from typing import Any

import cfnlint.helpers
from cfnlint.data.schemas.other import resources
from cfnlint.jsonschema import Validator
from cfnlint.rules.jsonschema.Base import BaseJsonSchema


class Configuration(BaseJsonSchema):
    """Check Base Resource Configuration"""

    id = "E3001"
    shortdesc = "Basic CloudFormation Resource Check"
    description = (
        "Making sure the basic CloudFormation resources are properly configured"
    )
    source_url = "https://github.com/aws-cloudformation/cfn-python-lint"
    tags = ["resources"]

    def __init__(self):
        super().__init__()
        self.validators = {
            "maxProperties": None,
            "propertyNames": None,
        }
        self.rule_set = {
            "maxProperties": "E3010",
            "propertyNames": "E3006",
        }
        self.child_rules = dict.fromkeys(list(self.rule_set.values()))
        self._schema = cfnlint.helpers.load_resource(resources, "configuration.json")

    @property
    def schema(self):
        return self._schema

    # pylint: disable=unused-argument
    def cfnresources(self, validator: Validator, _, instance: Any, schema):
        validator = self.extend_validator(
            validator, self.schema, context=validator.context.evolve()
        )
        for err in validator.iter_errors(instance):
            if err.rule is None:
                if err.validator in self.rule_set:
                    err.rule = self.child_rules[self.rule_set[err.validator]]
                elif not err.validator.startswith("fn") and err.validator != "ref":
                    err.rule = self
            yield err
