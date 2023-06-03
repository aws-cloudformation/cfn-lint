"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.resources.properties.CfnSchema import BaseCfnSchema


class FunctionZipfileRuntimeEnum(BaseCfnSchema):
    id = "E3677"
    shortdesc = "Validate Lambda using ZipFile requires an allowable runtime"
    description = (
        "Using the ZipFile attribute requires a javascript or "
        "python runtime to be specified"
    )
    tags = ["resources"]
    schema_path = "aws_lambda_function/zipfile_runtime_enum"
