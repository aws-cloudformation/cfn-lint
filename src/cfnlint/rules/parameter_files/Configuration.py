"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from cfnlint.rules.jsonschema.Base import BaseJsonSchema


class Configuration(BaseJsonSchema):

    id = "E0200"
    shortdesc = "Validate parameter file configuration"
    description = (
        "Validate if a parameter file has the correct syntax "
        "for one of the supported formats"
    )
    source_url = "https://github.com/aws-cloudformation/cfn-lint"
    tags = ["base"]
