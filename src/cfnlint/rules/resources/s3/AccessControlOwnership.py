"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from typing import Any

import cfnlint.data.schemas.extensions.aws_s3_bucket
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails


class AccessControlOwnership(CfnLintJsonSchema):
    """Check if the S3 Bucket Access Controls are set with Ownership rules"""

    id = "E3045"
    shortdesc = "Validate AccessControl are set with OwnershipControls"
    description = (
        "When using AccessControl other than private you must also "
        "configure OwnershipControls. The default is bucket owner "
        "enforced which disables ACLs."
    )
    source_url = "https://docs.aws.amazon.com/AmazonS3/latest/userguide/about-object-ownership.html"
    tags = ["resources", "s3"]

    def __init__(self):
        super().__init__(
            keywords=["Resources/AWS::S3::Bucket/Properties"],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_s3_bucket,
                filename="ownershipcontrols.json",
            ),
        )

    def message(self, instance: Any, err: ValidationError) -> str:
        return (
            "A bucket with 'AccessControl' set should also have "
            "at least one 'OwnershipControl' configured"
        )
