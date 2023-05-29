"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.jsonschema import ValidationError
from cfnlint.rules import CloudFormationLintRule
from cfnlint.template.template import Template


class AllowedValue(CloudFormationLintRule):
    """Check if parameters have a valid value"""

    id = "W2030"
    shortdesc = "Check if parameters have a valid value"
    description = (
        "Check if parameters have a valid value in case of an enumator. The Parameter's"
        " allowed values is based on the usages in property (Ref)"
    )
    source_url = "https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/cfn-resource-specification.md#allowedvalue"
    tags = ["parameters", "resources", "property", "allowed value"]

    def __init__(self):
        super().__init__()
        self.parameters = {}

    def initialize(self, cfn: Template):
        """Initialize the rule"""
        self.parameters = cfn.get_parameters()

    def validate(self, ref, enums):
        p = self.parameters.get(ref, {})
        if isinstance(p, dict):
            p_default = p.get("Default", None)
            if isinstance(p_default, (str, int, float, bool)):
                if p_default not in enums:
                    yield ValidationError(
                        f"{p_default!r} is not one of {enums!r}",
                        rule=self,
                        path_override=["Parameters", ref, "Default"],
                    )

            p_avs = p.get("AllowedValues", [])
            if isinstance(p_avs, list):
                for p_av in p_avs:
                    if p_av not in enums:
                        yield ValidationError(
                            f"{p_av!r} is not one of {enums!r}",
                            rule=self,
                            path_override=["Parameters", ref, "AllowedValues"],
                        )
