"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from typing import Any

from cfnlint.helpers import FUNCTIONS
from cfnlint.jsonschema import ValidationError, Validator
from cfnlint.rules.jsonschema import CfnLintKeyword


class DynamicReferenceSecret(CfnLintKeyword):
    """
    Check if Dynamic Reference Secure Strings are
    only used in the correct locations
    """

    id = "W1011"
    shortdesc = "Instead of REFing a parameter for a secret use a dynamic reference"
    description = (
        "Instead of REFing a parameter for a secret use a dynamic reference. "
        "Solutions like SSM parameter store and secrets manager provide "
        "better security of sercrets"
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/security-best-practices.html#creds"
    tags = ["functions", "dynamic reference", "ref"]

    def __init__(self) -> None:
        super().__init__(
            keywords=[
                "Resources/AWS::DirectoryService::MicrosoftAD/Properties/Password",
                "Resources/AWS::DirectoryService::SimpleAD/Properties/Password",
                "Resources/AWS::ElastiCache::ReplicationGroup/Properties/AuthToken",
                "Resources/AWS::IAM::User/Properties/LoginProfile/Password",
                "Resources/AWS::KinesisFirehose::DeliveryStream/Properties/RedshiftDestinationConfiguration/Password",
                "Resources/AWS::OpsWorks::App/Properties/AppSource/Password",
                "Resources/AWS::OpsWorks::Stack/Properties/RdsDbInstances/*/DbPassword",
                "Resources/AWS::OpsWorks::Stack/Properties/CustomCookbooksSource/Password",
                "Resources/AWS::RDS::DBCluster/Properties/MasterUserPassword",
                "Resources/AWS::RDS::DBInstance/Properties/MasterUserPassword",
                "Resources/AWS::Redshift::Cluster/Properties/MasterUserPassword",
            ]
        )
        self.parent_rules = ["E1020"]

    def validate(self, validator: Validator, _, instance: Any, schema: Any):
        functions = set(FUNCTIONS) - set(["Fn::If"])
        if any(p in functions for p in validator.context.path.path):
            return
        value = instance.get("Ref")

        if not validator.is_type(value, "string"):
            return

        if value in validator.context.parameters:
            yield ValidationError(
                "Use dynamic references over parameters for secrets", rule=self
            )
