"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.jsonschema._utils import ensure_list
from cfnlint.rules import CloudFormationLintRule


class AwsType(CloudFormationLintRule):
    """Check Conditions awsType values are correct"""

    id = "E1100"
    shortdesc = "Validate awsType(s) from the JSON schema"
    description = "This rule holds all the awsTypes that can be used in " "JSON schema"
    source_url = "https://github.com/aws-cloudformation/cfn-python-lint"
    tags = ["base"]

    def __init__(self) -> None:
        super().__init__()
        self.types = {
            "CfnConditions": "E8001",
            "CfnInitCommand": "E3009",
            "CfnInitFiles": "E3009",
            "CfnInitGroups": "E3009",
            "CfnInitPackages": "E3009",
            "CfnInitServices": "E3009",
            "CfnInitSources": "E3009",
            "CfnInitUsers": "E3009",
            "CfnMappings": "E7001",
            "CfnOutputs": "E6001",
            "CfnOutputExport": "E6102",
            "CfnOutputValue": "E6101",
            "CfnParameters": "E2001",
            "CfnResources": "E3001",
            "CfnResourceDeletionPolicy": "E3035",
            "CfnResourceType": "E3011",
            "CfnResourceProperties": "E3002",
            "CfnResourceUpdatePolicy": "E3016",
            "CfnResourceUpdateReplacePolicy": "E3036",
        }
        self.child_rules = dict.fromkeys(list(self.types.values()))

    # pylint: disable=unused-argument
    def awsType(self, validator, tS, instance, schema):
        tS = ensure_list(tS)
        for t in tS:
            rule = self.child_rules.get(self.types.get(t, ""))
            if not rule:
                return

            if hasattr(rule, t.lower()) and callable(getattr(rule, t.lower())):
                fn = getattr(rule, t.lower())
                yield from fn(validator, t, instance, schema)
            else:
                raise ValueError(f"{t.lower()!r} not found in ${rule.id!r}")
