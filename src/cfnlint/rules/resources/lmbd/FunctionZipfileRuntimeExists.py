"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.resources.properties.CfnSchema import BaseCfnSchema


class FunctionZipfileRuntimeExists(BaseCfnSchema):
    id = "E3678"
    shortdesc = "Using the ZipFile attribute requires a runtime to be specified"
    description = "Using the ZipFile attribute requires a runtime to be specified"
    tags = ["resources"]
    schema_path = "aws_lambda_function/zipfile_runtime_exists"
