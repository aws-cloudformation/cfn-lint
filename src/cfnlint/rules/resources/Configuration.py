"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import cfnlint.helpers
from cfnlint.data.schemas.other import resources
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
            "propertyNames": "E3011",
        }
        self.child_rules = dict.fromkeys(list(self.rule_set.values()))
        self._schema = cfnlint.helpers.load_resource(resources, "configuration.json")
        self.cfnresources = self.validate

    @property
    def schema(self):
        return self._schema
