"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from typing import Any

from cfnlint.jsonschema import Validator
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema


class UpdateReplacePolicyDeletionPolicyOnStatefulResourceTypes(CfnLintJsonSchema):
    """Check for UpdateReplacePolicy / DeletionPolicy"""

    id = "I3011"
    shortdesc = "Check stateful resources have a set UpdateReplacePolicy/DeletionPolicy"
    description = (
        "The default action when replacing/removing a resource is to "
        "delete it. This check requires you to explicitly set policies"
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-attribute-deletionpolicy.html"
    tags = ["resources", "updatereplacepolicy", "deletionpolicy"]

    def __init__(self):
        """Init"""
        super().__init__(
            keywords=["Resources/*"],
            all_matches=True,
        )

        self.config["types"] = [
            "AWS::Backup::BackupVault",
            "AWS::CloudFormation::Stack",
            "AWS::Cognito::UserPool",
            "AWS::DocDB::DBCluster",
            "AWS::DocDB::DBInstance",
            "AWS::DynamoDB::GlobalTable",
            "AWS::DynamoDB::Table",
            "AWS::EC2::Volume",
            "AWS::EFS::FileSystem",
            "AWS::EMR::Cluster",
            "AWS::ElastiCache::CacheCluster",
            "AWS::ElastiCache::ReplicationGroup",
            "AWS::Elasticsearch::Domain",
            "AWS::FSx::FileSystem",
            "AWS::KMS::Key",
            "AWS::Kinesis::Stream",
            "AWS::Logs::LogGroup",
            "AWS::Neptune::DBCluster",
            "AWS::Neptune::DBInstance",
            "AWS::OpenSearchService::Domain",
            "AWS::Organizations::Account",
            "AWS::QLDB::Ledger",
            "AWS::RDS::DBCluster",
            "AWS::RDS::DBInstance",
            "AWS::Redshift::Cluster",
            # "AWS::S3::Bucket", # can't be deleted without being empty
            "AWS::SDB::Domain",
            "AWS::SQS::Queue",
            "AWS::SecretsManager::Secret",
        ]

        self._schema = {"required": ["DeletionPolicy", "UpdateReplacePolicy"]}

    def validate(self, validator: Validator, s: Any, instance: Any, schema: Any):
        resource_type = instance.get("Type")

        if not isinstance(resource_type, str):
            return

        if resource_type not in self.config.get("types"):  # type: ignore
            return

        for err in super().validate(validator, s, instance, self._schema):
            err.message = (
                f"{err.message} (The default action when replacing/removing "
                "a resource is to delete it. Set explicit values for "
                "stateful resource)"
            )
            yield err
