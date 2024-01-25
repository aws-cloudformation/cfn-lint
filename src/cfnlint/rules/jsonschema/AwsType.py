"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
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
            "BackupBackupPlanLifecycle": "E3504",
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
            "AvailabilityZone": "W3010",
            "AvailabilityZones": "W3010",
            "IamIdentityPolicy": "E3510",
            "IamPolicyVersion": "W2511",
            "IamResourcePolicy": "E3512",
            "IamResourceEcrPolicy": "E3513",
            "IamRoleArn": "E3511",
            "LambdaRuntime": "E2531",
        }
        self.child_rules = dict.fromkeys(list(self.types.values()))

    # pylint: disable=unused-argument
    def awsType(self, validator, uI, instance, schema):
        rule = self.child_rules.get(self.types.get(uI, ""))
        if not rule:
            return

        if hasattr(rule, uI.lower()) and callable(getattr(rule, uI.lower())):
            validate = getattr(rule, uI.lower())
            yield from validate(validator, uI, instance, schema)
