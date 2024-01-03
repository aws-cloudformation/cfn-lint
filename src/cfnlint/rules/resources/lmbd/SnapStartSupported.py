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
        self.regions = [
            "us-east-2",
            "us-east-1",
            "us-west-1",
            "us-west-2",
            "af-south-1",
            "ap-east-1",
            "ap-southeast-3",
            "ap-south-1",
            "ap-northeast-2",
            "ap-northeast-3",
            "ap-southeast-1",
            "ap-southeast-2",
            "ap-northeast-1",
            "ca-central-1",
            "eu-central-1",
            "eu-west-1",
            "eu-west-2",
            "eu-south-1",
            "eu-west-3",
            "eu-north-1",
            "me-south-1",
            "sa-east-1",
        ]

    def match_resource_properties(self, properties, _, path, cfn):
        """Check CloudFormation Properties"""
        matches = []

        for region in cfn.regions:
            for scenario in cfn.get_object_without_conditions(
                properties, ["Runtime", "SnapStart"], region
            ):
                props = scenario.get("Object")

                runtime = props.get("Runtime")
                snap_start = props.get("SnapStart")
                if not snap_start:
                    if self.child_rules["I2530"]:
                        matches.extend(
                            self.child_rules["I2530"].validate(
                                runtime, path, region, self.regions
                            )
                        )
                    continue

                if region not in self.regions:
                    matches.append(
                        RuleMatch(
                            path + ["SnapStart"],
                            f"Region {region} does not support SnapStart enabled functions",
                        )
                    )

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
