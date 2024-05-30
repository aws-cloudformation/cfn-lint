"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from typing import Any

from cfnlint.jsonschema import ValidationError, Validator
from cfnlint.rules.functions._BaseFn import BaseFn


class DynamicReferenceSecureString(BaseFn):
    id = "E1027"
    shortdesc = "Check dynamic references secure strings are in supported locations"
    description = (
        "Dynamic References Secure Strings are only supported for a small set of"
        " resource properties.  Validate that they are being used in the correct"
        " location when checking values and Fn::Sub in resource properties. Currently"
        " doesn't check outputs, maps, conditions, parameters, and descriptions."
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/dynamic-references.html"
    tags = ["functions", "dynamic reference"]

    def __init__(self):
        """Init"""
        super().__init__()
        self.exceptions = [
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

    def validate(self, validator: Validator, s: Any, instance: Any, schema: Any):
        if validator.context.path.cfn_path_string in self.exceptions:
            return

        yield ValidationError(
            (
                f"Dynamic reference {instance!r} to SSM secure strings "
                "can only be used in resource properties"
            ),
            rule=self,
        )
