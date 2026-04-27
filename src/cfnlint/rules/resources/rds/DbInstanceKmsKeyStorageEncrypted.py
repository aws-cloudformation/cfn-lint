"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.extensions.aws_rds_dbinstance
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class DbInstanceKmsKeyStorageEncrypted(CfnLintJsonSchema):
    id = "E3720"
    shortdesc = "Validate StorageEncrypted is set when KmsKeyId is specified"
    description = (
        "When specifying a KmsKeyId for a non-custom engine RDS DBInstance, "
        "StorageEncrypted must be set to true. Custom engines (custom-*) "
        "handle encryption implicitly and do not require StorageEncrypted."
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-rds-dbinstance.html"
    tags = ["resources", "rds"]

    def __init__(self) -> None:
        super().__init__(
            keywords=[
                "Resources/AWS::RDS::DBInstance/Properties",
            ],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_rds_dbinstance,
                filename="kmskey_storageencrypted.json",
            ),
        )

    def message(self, instance: Any, err: ValidationError) -> str:
        return err.message
