"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema


class FunctionZipfileRuntimeExists(CfnLintJsonSchema):
    id = "E3678"
    shortdesc = "Using the ZipFile attribute requires a runtime to be specified"
    description = "Using the ZipFile attribute requires a runtime to be specified"
    tags = ["resources"]

    def __init__(self) -> None:
        super().__init__(keywords=["aws_lambda_function/zipfile_runtime_exists"])
