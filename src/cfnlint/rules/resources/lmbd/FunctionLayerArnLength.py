"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import cfnlint.data.schemas.extensions.aws_lambda_function
from cfnlint.rules.jsonschema.CfnLintJsonSchema import SchemaDetails
from cfnlint.rules.jsonschema.CfnLintJsonSchemaRegional import CfnLintJsonSchemaRegional


class FunctionLayerArnLength(CfnLintJsonSchemaRegional):
    id = "E3716"
    shortdesc = "Validate Lambda layer ARN length based on region"
    description = (
        "Validates the Lambda layer ARN length based on region. "
        "ARN length varies by partition due to partition and region name length."
    )
    tags = ["resources", "lambda"]

    def __init__(self) -> None:
        super().__init__(
            keywords=["Resources/AWS::Lambda::Function/Properties/Layers/*"],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_lambda_function,
                filename="layers_maxlength.json",
            ),
        )
