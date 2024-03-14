"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from datetime import date
from typing import Any

from cfnlint.jsonschema import ValidationError, Validator
from cfnlint.rules.jsonschema.CfnLintKeyword import CfnLintKeyword


class PolicyVersion(CfnLintKeyword):
    """Check if IAM Policy Version is correct"""

    id = "W2511"
    shortdesc = "Check IAM Resource Policies syntax"
    description = (
        "See if the elements inside an IAM Resource policy are configured correctly."
    )
    source_url = "https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements.html"
    tags = ["properties", "iam"]

    def __init__(self) -> None:
        super().__init__(["AWS::IAM::Policy/Properties/PolicyDocument/Version"])

    # pylint: disable=unused-argument
    def validate(self, validator: Validator, _, instance: Any, schema):
        if not isinstance(instance, (date, str)):
            return

        if instance in ["2008-10-17", date(2008, 10, 17)]:
            yield ValidationError(
                "IAM Policy Version should be updated to '2012-10-17'",
                rule=self,
            )
