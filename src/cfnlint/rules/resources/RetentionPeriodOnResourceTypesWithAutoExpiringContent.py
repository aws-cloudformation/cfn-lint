"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.extensions.aws_rds_dbinstance
from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class RetentionPeriodOnResourceTypesWithAutoExpiringContent(CfnLintJsonSchema):
    """Check Base Resource Configuration"""

    id = "I3013"
    shortdesc = (
        "Check resources with auto expiring content have explicit retention period"
    )
    description = (
        "The behaviour for data retention is different across AWS Services.If no"
        " retention period is specified the default for some services is to delete the"
        " data after a period of time.This check requires you to explicitly set the"
        " retention period for those resources to avoid unexpected data losses"
    )
    source_url = "https://github.com/aws-cloudformation/cfn-lint"
    tags = ["resources", "retentionperiod"]

    def __init__(self) -> None:
        super().__init__(
            [
                "Resources/AWS::RDS::DBInstance/Properties",
                "Resources/AWS::Kinesis::Stream/Properties",
                "Resources/AWS::SQS::Queue/Properties",
                "Resources/AWS::DocDB::DBCluster/Properties",
                "Resources/AWS::Synthetics::Canary/Properties",
                "Resources/AWS::Redshift::Cluster/Properties",
                "Resources/AWS::RDS::DBInstance/Properties",
                "Resources/AWS::RDS::DBCluster/Properties",
            ],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_rds_dbinstance,
                filename="backupretentionperiod.json",
            ),
        )
        self._rds_schema = self._schema
        self._properties: dict[str, list[dict[str, str]]] = {
            "AWS::Kinesis::Stream": [
                {
                    "Attribute": "RetentionPeriodHours",
                    "SourceUrl": "http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-kinesis-stream.html#cfn-kinesis-stream-retentionperiodhours",
                }
            ],
            "AWS::SQS::Queue": [
                {
                    "Attribute": "MessageRetentionPeriod",
                    "SourceUrl": "http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-sqs-queues.html#aws-sqs-queue-msgretentionperiod",
                }
            ],
            "AWS::DocDB::DBCluster": [
                {
                    "Attribute": "BackupRetentionPeriod",
                    "SourceUrl": "http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-docdb-dbcluster.html#cfn-docdb-dbcluster-backupretentionperiod",
                }
            ],
            "AWS::Synthetics::Canary": [
                {
                    "Attribute": "SuccessRetentionPeriod",
                    "SourceUrl": "http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-synthetics-canary.html#cfn-synthetics-canary-successretentionperiod",
                },
                {
                    "Attribute": "FailureRetentionPeriod",
                    "SourceUrl": "http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-synthetics-canary.html#cfn-synthetics-canary-failureretentionperiod",
                },
            ],
            "AWS::Redshift::Cluster": [
                {
                    "Attribute": "AutomatedSnapshotRetentionPeriod",
                    "SourceUrl": "http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-redshift-cluster.html#cfn-redshift-cluster-automatedsnapshotretentionperiod",
                }
            ],
            "AWS::RDS::DBInstance": [
                {
                    "Attribute": "BackupRetentionPeriod",
                    "SourceUrl": "http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-rds-database-instance.html#cfn-rds-dbinstance-backupretentionperiod",
                }
            ],
            "AWS::RDS::DBCluster": [
                {
                    "Attribute": "BackupRetentionPeriod",
                    "SourceUrl": "http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-backuprententionperiod",
                }
            ],
        }

    def message(self, instance: Any, err: ValidationError) -> str:
        return (
            f"{err.message} (The default retention period will delete "
            "the data after a pre-defined time. Set an explicit "
            "values to avoid data loss on resource)"
        )

    def validate(
        self, validator: Validator, keywords: Any, instance: Any, schema: dict[str, Any]
    ) -> ValidationResult:
        if len(validator.context.path.cfn_path) < 1:
            return

        resource_type = validator.context.path.cfn_path[1]

        if resource_type != "AWS::RDS::DBInstance":
            required = []
            for properties in self._properties.get(resource_type, []):
                property = properties.get("Attribute")
                if property:
                    required.append(property)

            self._schema = {"required": required}
        else:
            self._schema = self._rds_schema

        yield from super().validate(validator, keywords, instance, schema)
