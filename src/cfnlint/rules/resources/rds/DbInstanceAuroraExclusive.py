"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.extensions.aws_rds_dbinstance
from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class DbInstanceAuroraExclusive(CfnLintJsonSchema):
    id = "E3682"
    shortdesc = "Validate when using Aurora certain properies aren't required"
    description = (
        "When creating an aurora DBInstance don't specify "
        "'AllocatedStorage', 'BackupRetentionPeriod', 'CopyTagsToSnapshot', "
        "'DeletionProtection', 'EnableIAMDatabaseAuthentication', "
        "'MasterUserPassword', or 'StorageEncrypted'"
    )
    tags = ["resources"]

    def __init__(self) -> None:
        super().__init__(
            keywords=["Resources/AWS::RDS::DBInstance/Properties"],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_rds_dbinstance,
                filename="aurora_exclusive.json",
            ),
        )

    def message(self, instance: Any, err: ValidationError) -> str:
        keys = [
            "AllocatedStorage",
            "BackupRetentionPeriod",
            "CopyTagsToSnapshot",
            "DeletionProtection",
            "EnableIAMDatabaseAuthentication",
            "MasterUserPassword",
            "StorageEncrypted",
        ]
        extra = []
        for property in instance.keys():
            if property in keys:
                extra.append(property)

        return f"Additional properties are not allowed ({extra!r})"

    def validate(
        self, validator: Validator, keywords: Any, instance: Any, schema: dict[str, Any]
    ) -> ValidationResult:
        if not validator.is_type(instance, "object"):
            return

        if validator.is_type(instance.get("Engine"), "string"):
            instance["Engine"] = instance["Engine"].lower()

        yield from super().validate(validator, keywords, instance, schema)
