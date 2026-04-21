"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

import regex as re

from cfnlint.jsonschema import Validator
from cfnlint.rules.formats.FormatKeyword import FormatKeyword


class S3BucketName(FormatKeyword):
    id = "E1161"
    shortdesc = "Validate S3 bucket name format"
    description = "Validate S3 bucket name format for ref/getatt and string values"
    tags = []
    source_url = "https://github.com/aws-cloudformation/cfn-lint/blob/main/docs/format_keyword.md#AWS::S3::Bucket.Name"

    def __init__(self):
        super().__init__(
            format="AWS::S3::Bucket.Name",
            pattern=r"^(?![.\-])(?!.*\.\.)(?!.*\-\.)(?!.*\.\-)[a-z0-9.\-]{3,63}(?<![.\-])$",
        )

    def format(self, validator: Validator, instance: Any) -> bool:
        if not isinstance(instance, str):
            return True

        if (
            instance == ""
            and validator.context.path.cfn_path_string
            == "Resources/AWS::S3::Bucket/Properties/BucketName"
        ):
            return True

        if re.match(self.pattern, instance):
            return True

        return False
