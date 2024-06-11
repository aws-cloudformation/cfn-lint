"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from collections import deque
from typing import Any

from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules.jsonschema.CfnLintKeyword import CfnLintKeyword


class AccessControlObsolete(CfnLintKeyword):
    """Check if the S3 Bucket Access Controls are configured"""

    id = "W3045"
    shortdesc = "Controlling access to an S3 bucket should be done with bucket policies"
    description = (
        "Nearly all access control configurations can be more successfully achieved "
        "with bucket policies. Consider using bucket policies instead of access "
        "control."
    )
    source_url = "https://docs.aws.amazon.com/AmazonS3/latest/userguide/about-object-ownership.html"
    tags = ["resources", "s3"]

    def __init__(self):
        super().__init__(["Resources/AWS::S3::Bucket/Properties"])

    def validate(
        self, validator: Validator, _, instance: Any, schema: dict[str, Any]
    ) -> ValidationResult:
        property_sets = validator.cfn.get_object_without_conditions(
            instance, ["AccessControl"]
        )

        for property_set in property_sets:
            props = property_set.get("Object")
            access_control = props.get("AccessControl", None)
            if access_control:
                yield ValidationError(
                    (
                        "'AccessControl' is a legacy property. Consider "
                        "using 'AWS::S3::BucketPolicy' instead"
                    ),
                    path=deque(["AccessControl"]),
                    instance=access_control,
                )
