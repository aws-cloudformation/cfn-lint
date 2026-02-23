"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from typing import Any

from cfnlint.helpers import VALID_PARAMETER_TYPES
from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules.jsonschema import CfnLintKeyword


class UnsupportedParameterType(CfnLintKeyword):
    """Check if Parameters use unsupported types"""

    id = "W2002"
    shortdesc = "Parameter type is not officially supported by CloudFormation"
    description = (
        "CloudFormation accepts any AWS::SSM::Parameter::Value<> or List<> pattern, "
        "but only validates specific types. Using unsupported types may work but "
        "CloudFormation will not validate the parameter values."
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cloudformation-supplied-parameter-types.html"
    tags = ["parameters"]

    def __init__(self) -> None:
        super().__init__(keywords=["Parameters/*/Type"])

    def validate(
        self, validator: Validator, s: Any, instance: Any, schema: Any
    ) -> ValidationResult:
        if not validator.is_type(instance, "string"):
            return

        # Check if it's an SSM or List type but not in the supported list
        if (
            instance.startswith("AWS::SSM::Parameter::Value<")
            or instance.startswith("List<")
        ) and instance not in VALID_PARAMETER_TYPES:
            yield ValidationError(
                f"{instance!r} is not an officially documented "
                "CloudFormation parameter type. While CloudFormation may "
                "accept this type, it will not validate the parameter value.",
                rule=self,
            )
