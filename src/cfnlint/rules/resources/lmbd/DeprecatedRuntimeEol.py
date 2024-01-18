"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from datetime import datetime

from cfnlint.jsonschema import ValidationError
from cfnlint.rules import CloudFormationLintRule


class DeprecatedRuntimeEol(CloudFormationLintRule):
    """Check if EOL Lambda Function Runtimes are used"""

    id = "W2531"
    shortdesc = "Check if EOL Lambda Function Runtimes are used"
    description = (
        "Check if an EOL Lambda Runtime is specified and give a warning if used. "
    )
    source_url = (
        "https://docs.aws.amazon.com/lambda/latest/dg/runtime-support-policy.html"
    )
    tags = ["resources", "lambda", "runtime"]

    def __init__(self):
        """Init"""
        super().__init__()
        self.current_date = datetime.today()

    # pylint: disable=unused-argument
    def lambdaruntime(self, runtime, runtime_data):
        if not runtime_data:
            return
        if (
            datetime.strptime(runtime_data["eol"], "%Y-%m-%d") < self.current_date
            and datetime.strptime(runtime_data["deprecated"], "%Y-%m-%d")
            > self.current_date
        ):
            yield ValidationError(
                (
                    f"EOL runtime {runtime!r} specified. Runtime is EOL since "
                    f"{runtime_data['eol']!r} and updating "
                    f"will be disabled at {runtime_data['deprecated']!r}. "
                    f"Please consider updating to {runtime_data['successor']!r}"
                ),
                rule=self,
            )
