"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from typing import Any, Iterator

from cfnlint.jsonschema import ValidationError, Validator
from cfnlint.rules.functions._BaseFn import BaseFn, singular_types


class GetStackOutput(BaseFn):
    """Check if GetStackOutput values are correct"""

    id = "E1033"
    shortdesc = "GetStackOutput validation of parameters"
    description = "Making sure the GetStackOutput function is properly configured"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference.html"
    tags = ["functions", "getstackoutput"]

    def __init__(self) -> None:
        super().__init__(
            "Fn::GetStackOutput",
            singular_types,
        )

    def fn_getstackoutput(
        self, validator: Validator, s: Any, instance: Any, schema: Any
    ) -> Iterator[ValidationError]:
        yield from super().validate(validator, s, instance, schema)
