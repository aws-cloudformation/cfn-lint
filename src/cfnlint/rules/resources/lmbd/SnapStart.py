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

    def _check_value(self, value, path, **kwargs):
        lambda_versions = kwargs["lambda_versions"]
        cfn = kwargs["cfn"]

        if value != "PublishedVersions":
            return []

        # SnapStart is enabled, validate if version is attached
        matches = [
            v
            for v in lambda_versions
            if any(edge == path[1] for edge in cfn.graph.graph.neighbors(v))
        ]

        if len(matches) < 1:
            return [
                RuleMatch(
                    path,
                    "SnapStart is enabled but Lambda version is not attached",
                )
            ]

        return []

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

            matches.extend(
                cfn.check_value(
                    snap_start,
                    "ApplyOn",
                    path,
                    check_value=self._check_value,
                    lambda_versions=lambda_versions,
                    cfn=cfn,
                )
            )

        return matches
