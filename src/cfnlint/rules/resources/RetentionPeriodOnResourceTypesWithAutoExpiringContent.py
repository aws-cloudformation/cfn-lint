"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import regex as re
from collections import deque
from typing import Any, Dict

from cfnlint.jsonschema import ValidationError, Validator
from cfnlint.rules.jsonschema.Base import BaseJsonSchema
from cfnlint.schema.manager import PROVIDER_SCHEMA_MANAGER


class RetentionPeriodOnResourceTypesWithAutoExpiringContent(BaseJsonSchema):
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
    source_url = "https://github.com/aws-cloudformation/cfn-python-lint"
    tags = ["resources", "retentionperiod"]

    def __init__(self) -> None:
        super().__init__()
        self._properties = {
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
                    "CheckAttribute": "Engine",
                    "CheckAttributeRegex": re.compile("^((?!aurora).)*$"),
                }
            ],
            "AWS::RDS::DBCluster": [
                {
                    "Attribute": "BackupRetentionPeriod",
                    "SourceUrl": "http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-backuprententionperiod",
                }
            ],
        }

    def _schema(self, resource_type: str):
        required = []
        for properties in self._properties.get(resource_type):
            property = properties.get("Attribute")
            if property:
                required.append(property)

        return {"required": required}

    # pylint: disable=unused-argument
    def backupretentionperiod(
        self,
        validator: Validator,
        resource_type: str,
        instance: Any,
        schema: Dict[str, Any],
    ):
        resource_type = (
            validator.cfn.template.get(validator.context.path[0])
            .get(validator.context.path[1])
            .get("Type")
        )
        if not validator.is_type(resource_type, "string"):
            return

        validator = validator.evolve(schema=self._schema(resource_type=resource_type))
        for err in validator.iter_errors(instance):
            err.rule = self
            err.message = (
                "The default retention period will delete the data after a pre-defined time. Set an explicit values to avoid data loss on resource. "
                + err.message
            )
            yield err
