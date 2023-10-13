"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules import CloudFormationLintRule, RuleMatch


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

    def __init__(self):
        super().__init__()
        self.resource_property_types.append("AWS::Lambda::Function")

    def match_resource_properties(self, properties, _, path, cfn):
        """Check CloudFormation Properties"""
        matches = []

        for scenario in cfn.get_object_without_nested_conditions(properties, path):
            props = scenario.get("Object")

            runtime = props.get("Runtime")
            if not runtime:
                continue
            # future proofing this rule.  This will apply to newer java runtimes
            # so we are validating its java and not java8.al2
            if (
                runtime
                and (not runtime.startswith("java"))
                and runtime not in ["java8.al2", "java8"]
            ):
                continue

            snap_start = props.get("SnapStart")

            if snap_start:
                if snap_start.get("ApplyOn") is not None:
                    continue

            matches.append(
                RuleMatch(
                    path,
                    f"When using {runtime} configure SnapStart",
                )
            )

        return matches
