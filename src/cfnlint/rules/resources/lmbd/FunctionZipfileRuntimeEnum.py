"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""


from __future__ import annotations

from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema



class FunctionZipfileRuntimeEnum(CfnLintJsonSchema):
    id = "E3677"
    shortdesc = "Validate Lambda using ZipFile requires an allowable runtime"
    description = (
        "Using the ZipFile attribute requires a javascript or "
        "python runtime to be specified"
    )
    tags = ["resources"]

    def __init__(self) -> None:
        super().__init__(keywords=["aws_lambda_function/zipfile_runtime_enum"])
