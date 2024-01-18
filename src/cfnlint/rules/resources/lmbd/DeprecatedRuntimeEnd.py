"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from datetime import datetime

from cfnlint.data import AdditionalSpecs
from cfnlint.helpers import load_resource
from cfnlint.jsonschema import ValidationError
from cfnlint.rules import CloudFormationLintRule


class DeprecatedRuntimeEnd(CloudFormationLintRule):
    """Check if EOL Lambda Function Runtimes are used"""

    id = "E2531"
    shortdesc = "Check if EOL Lambda Function Runtimes are used"
    description = (
        "Check if an EOL Lambda Runtime is specified and give an error if used. "
    )
    source_url = (
        "https://docs.aws.amazon.com/lambda/latest/dg/runtime-support-policy.html"
    )
    tags = ["resources", "lambda", "runtime"]

    def __init__(self):
        """Init"""
        super().__init__()
        self.child_rules = {
            "W2531": None,
        }
        self.current_date = datetime.today()
        self.deprecated_runtimes = load_resource(
            AdditionalSpecs, "LmbdRuntimeLifecycle.json"
        )

    # pylint: disable=unused-argument
    def lambdaruntime(self, validator, v, runtime, schema):
        runtime_data = self.deprecated_runtimes.get(runtime)
        if not runtime_data:
            return
        if (
            datetime.strptime(runtime_data["deprecated"], "%Y-%m-%d")
            < self.current_date
        ):
            yield ValidationError(
                (
                    f"Deprecated runtime {runtime!r} specified. Updating "
                    f"disabled since {runtime_data['deprecated']!r}. "
                    f"Please consider updating to {runtime_data['successor']!r}"
                ),
                rule=self,
            )

        if self.child_rules["W2531"]:
            yield from self.child_rules["W2531"].lambdaruntime(runtime, runtime_data)
