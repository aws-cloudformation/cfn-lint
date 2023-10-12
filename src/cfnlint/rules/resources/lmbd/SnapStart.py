"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules import CloudFormationLintRule, RuleMatch


class SnapStart(CloudFormationLintRule):
    """Check if the settings of multiple subscriptions are included for one LogGroup"""

    id = "W2530"
    shortdesc = "Validate that SnapStart is properly configured"
    description = (
        "To properly leverage SnapStart, you must configure both the lambda function "
        "and attach a Lambda version resource"
    )
    source_url = "https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md#user-content-cloudwatchlogs"
    tags = ["resources", "lambda"]

    def __init__(self):
        super().__init__()
        self.resource_property_types.append("AWS::Lambda::Function")
        self.snapstart_runtimes = ["java11", "java17"]

    def match_resource_properties(self, properties, _, path, cfn):
        """Check CloudFormation Properties"""
        matches = []

        # if there is no graph we can't validate
        if not cfn.graph:
            return matches

        lambda_versions = cfn.get_resources(["AWS::Lambda::Version"])

        for scenario in cfn.get_object_without_conditions(
            properties, ["SnapStart", "Runtime"]
        ):
            props = scenario.get("Object")

            if props.get("Runtime") not in self.snapstart_runtimes:
                continue

            snap_start = props.get("SnapStart")
            if not snap_start:
                continue

            if snap_start.get("ApplyOn") != "PublishedVersions":
                continue

            found = False
            # SnapStart is enabled, no validate if version is attached
            for version in lambda_versions:
                if any(edge == path[1] for edge in cfn.graph.graph.neighbors(version)):
                    found = True

            if not found:
                matches.append(
                    RuleMatch(
                        path + ["SnapStart", "ApplyOn"],
                        "SnapStart is enabled but Lambda version is not attached",
                    )
                )

        return matches
