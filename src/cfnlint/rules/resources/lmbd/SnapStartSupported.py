"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules import CloudFormationLintRule, RuleMatch


class SnapStartSupported(CloudFormationLintRule):
    """Check if Lambda function using SnapStart has the correct runtimes"""

    id = "E2530"
    shortdesc = "SnapStart supports the configured runtime"
    description = (
        "To properly leverage SnapStart, you must have a runtime of Java11 or greater"
    )
    source_url = "https://docs.aws.amazon.com/lambda/latest/dg/snapstart.html"
    tags = ["resources", "lambda"]

    def __init__(self):
        super().__init__()
        self.resource_property_types.append("AWS::Lambda::Function")
        self.child_rules = {"I2530": None}

    def match_resource_properties(self, properties, _, path, cfn):
        """Check CloudFormation Properties"""
        matches = []

        for scenario in cfn.get_object_without_nested_conditions(properties, path):
            props = scenario.get("Object")

            runtime = props.get("Runtime")
            snap_start = props.get("SnapStart")
            if not snap_start:
                if self.child_rules["I2530"]:
                    matches.extend(self.child_rules["I2530"].validate(runtime, path))
                continue

            if snap_start.get("ApplyOn") != "PublishedVersions":
                continue

            # Validate runtime is a string before using startswith
            if not isinstance(runtime, str):
                continue

            if (
                runtime
                and (not runtime.startswith("java"))
                and runtime not in ["java8.al2", "java8"]
            ):
                matches.append(
                    RuleMatch(
                        path + ["SnapStart", "ApplyOn"],
                        f"{runtime} is not supported for SnapStart enabled functions",
                    )
                )

        return matches
