"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import cfnlint.data.schemas.extensions.aws_rds_dbinstance
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
            keywords=["AWS::RDS::DBInstance/Properties"],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_rds_dbinstance,
                filename="aurora_exclusive.json",
            ),
            all_matches=True,
        )

    def validate(self, validator, keywords, instance, schema):
        if not validator.is_type(instance, "object"):
            return

        if validator.is_type(instance.get("Engine"), "string"):
            instance["Engine"] = instance["Engine"].lower()

        for err in super().validate(validator, keywords, instance, schema):
            if err.schema is False:
                err.message = (
                    "Additional properties are not allowed "
                    f"{err.path[0]!r} when creating an Aurora instance"
                )

            yield err
