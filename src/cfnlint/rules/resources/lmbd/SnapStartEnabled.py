"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

from cfnlint.jsonschema import ValidationError
from cfnlint.rules import CloudFormationLintRule


class SnapStartEnabled(CloudFormationLintRule):
    """Check if the SnapStart is enabled for certain java runtimes"""

    id = "I2530"
    shortdesc = "Validate that SnapStart is configured for >= Java11 runtimes"
    description = (
        "SnapStart is a no-cost feature that can increase performance up to 10x. "
        "Enable SnapStart for Java 11 and greater runtimes"
    )
    source_url = "https://docs.aws.amazon.com/lambda/latest/dg/snapstart.html"
    tags = ["resources", "lambda"]

    def validate(self, runtime):
        if not isinstance(runtime, str):
            return

        if not (runtime.startswith("java")) or runtime in ["java8.al2", "java8"]:
            return

        yield ValidationError(
            f"{runtime!r} runtime should consider using 'SnapStart'",
            path=deque(["SnapStart", "ApplyOn"]),
            rule=self,
        )
