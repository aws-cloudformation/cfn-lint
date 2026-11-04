"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.extensions.aws_rds_dbcluster
from cfnlint.jsonschema import ValidationResult, Validator
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails

# Schema paths of the two Iops requirements in multiaz.json "then.allOf"
_IOPS_FOR_PROVISIONED_STORAGE = ["then", "allOf", 0, "then", "required"]
_IOPS_FOR_NO_STORAGE_TYPE = ["then", "allOf", 1, "then", "required"]


class DbClusterMultiAz(CfnLintJsonSchema):
    id = "E3692"
    shortdesc = "Validate Multi-AZ DB cluster configuration"
    description = (
        "When creating a Multi-AZ DB Cluster there are required fields and "
        "the allowed values are different"
    )
    tags = ["resources"]
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbcluster.html#cfn-rds-dbcluster-engineversion"

    def __init__(self) -> None:
        super().__init__(
            keywords=["Resources/AWS::RDS::DBCluster/Properties"],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_rds_dbcluster,
                filename="multiaz.json",
            ),
            all_matches=True,
        )

    # Rewrite messages for forbidden properties and for conditional Iops
    def validate(
        self, validator: Validator, keywords: Any, instance: Any, schema: dict[str, Any]
    ) -> ValidationResult:
        for err in super().validate(validator, keywords, instance, schema):
            schema_path = list(err.schema_path)
            if schema_path == _IOPS_FOR_PROVISIONED_STORAGE:
                err.message = (
                    "'Iops' is a required property when 'StorageType' is "
                    f"{err.instance.get('StorageType')!r}"
                )
            elif schema_path == _IOPS_FOR_NO_STORAGE_TYPE:
                err.message = (
                    "Set 'Iops' or set 'StorageType' to 'gp3'; without either, "
                    "RDS uses gp2 storage, which Multi-AZ DB clusters do not "
                    "support"
                )
            elif err.schema is False:
                if schema_path[:2] == ["then", "then"]:
                    err.message = (
                        f"{err.path[0]!r} is not allowed on a Multi-AZ DB "
                        "cluster read replica (ReplicationSourceIdentifier is set)"
                    )
                else:
                    err.message = (
                        "Additional properties are not allowed "
                        f"{err.path[0]!r} when creating Multi-AZ cluster"
                    )

            yield err
