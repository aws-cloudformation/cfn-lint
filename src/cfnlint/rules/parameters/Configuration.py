"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.data.schemas.other import parameters as schema_parameters
from cfnlint.helpers import load_resource
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
        self.cfnparameters = self.validate
        self._schema = load_resource(schema_parameters, "configuration.json")

    @property
    def schema(self):
        return self._schema
