"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import cfnlint.data.schemas.extensions.aws_fsx_filesystem
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class FileSystemStorageCapacity(CfnLintJsonSchema):
    id = "E3725"
    shortdesc = "Validate FSx file system StorageCapacity based on FileSystemType"
    description = (
        "The allowed StorageCapacity range depends on the FileSystemType. "
        "Windows file systems allow 32 to 65536 GiB and OpenZFS 64 to 524288 GiB. "
        "Lustre has a minimum of 1200 GiB and ONTAP a minimum of 1024 GiB, with no "
        "static maximum (the ceiling is an adjustable, account level quota)."
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-fsx-filesystem.html#cfn-fsx-filesystem-storagecapacity"
    tags = ["resources", "fsx"]

    def __init__(self) -> None:
        super().__init__(
            keywords=[
                "Resources/AWS::FSx::FileSystem/Properties",
            ],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_fsx_filesystem,
                filename="storage_capacity.json",
            ),
        )

    def message(self, instance: Any, err: ValidationError) -> str:
        fs_type = instance.get("FileSystemType")
        return f"{err.message} for {fs_type!r} file systems"
