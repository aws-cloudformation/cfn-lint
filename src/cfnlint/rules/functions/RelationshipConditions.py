"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint._typing import RuleMatches
from cfnlint.rules import CloudFormationLintRule, RuleMatch
from cfnlint.template import Template


class RelationshipConditions(CloudFormationLintRule):
    """Check if Ref/GetAtt values are available via conditions"""

    id = "W1001"
    shortdesc = "Ref/GetAtt to resource that is available when conditions are applied"
    description = (
        "Check the Conditions that affect a Ref/GetAtt to make sure "
        "the resource being related to is available when there is a resource "
        "condition."
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-ref.html"
    tags = ["conditions", "resources", "relationships", "ref", "getatt", "sub"]

    def match(self, cfn: Template) -> RuleMatches:
        """Check CloudFormation Ref/GetAtt for Conditions"""

        matches: RuleMatches = []
        if cfn.graph is None:
            return matches
        for edge in cfn.graph.graph.edges.data():
            source, destination, data = edge

            # Depends on is already covered
            if data.get("label") == "DependsOn":
                continue
            # Double check the destination is a in the graph
            if destination not in cfn.graph.graph.nodes:
                continue
            # If the destination isn't a resource it won't matter
            if "Resource" != cfn.graph.graph.nodes[destination]["type"]:
                continue

            path = [
                f"{cfn.graph.graph.nodes[source].get('type')}s",
                source.replace("Output-", ""),
            ] + data["source_paths"]
            scenarios = cfn.is_resource_available(path, destination)

            for scenario in scenarios:
                # pylint: disable=consider-using-f-string
                scenario_text = " and ".join(
                    [
                        "when condition '%s' is %s" % (k, v)
                        for (k, v) in scenario.items()
                    ]
                )

                message = (
                    f"{data.get('label')} to resource "
                    f"{destination!r} that may not be available "
                    f"{scenario_text} at {'/'.join(map(str, path))}"
                )
                matches.append(RuleMatch(path, message))

        return matches
