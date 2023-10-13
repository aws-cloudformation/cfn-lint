"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules import CloudFormationLintRule, RuleMatch


class SnapStart(CloudFormationLintRule):
    """Check if Lambda SnapStart is properly configured"""

    id = "W2530"
    shortdesc = "Validate that SnapStart is properly configured"
    description = (
        "To properly leverage SnapStart, you must configure both the lambda function "
        "and attach a Lambda version resource"
    )
    source_url = "https://docs.aws.amazon.com/lambda/latest/dg/snapstart.html"
    tags = ["resources", "lambda"]

    def __init__(self):
        super().__init__()
        self.resource_property_types.append("AWS::Lambda::Function")

    def match_resource_properties(self, properties, _, path, cfn):
        """Check CloudFormation Properties"""
        matches = []

        # if there is no graph we can't validate
        if not cfn.graph:
            return matches

        lambda_versions = cfn.get_resources(["AWS::Lambda::Version"])

        for scenario in cfn.get_object_without_conditions(properties, ["SnapStart"]):
            props = scenario.get("Object")

            snap_start = props.get("SnapStart")
            if not snap_start:
                continue

            # Get safe removes any conditions nested
            # since we aren't checking runtimes we just need to know if
            # there is a scenario in which PublishedVersions is present
            for apply_on in snap_start.get_safe("ApplyOn"):
                if apply_on[0] != "PublishedVersions":
                    continue

                # SnapStart is enabled, validate if version is attached
                matches = [
                    v
                    for v in lambda_versions
                    if any(edge == path[1] for edge in cfn.graph.graph.neighbors(v))
                ]

                if len(matches) < 1:
                    matches.append(
                        RuleMatch(
                            path + ["SnapStart", apply_on[1]],
                            "SnapStart is enabled but Lambda version is not attached",
                        )
                    )

        return matches
