"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint._typing import RuleMatches
from cfnlint.rules import CloudFormationLintRule, RuleMatch
from cfnlint.template import Template


class CircularDependency(CloudFormationLintRule):
    """Check if Resources have a circular dependency"""

    id = "E3004"
    shortdesc = "Resource dependencies are not circular"
    description = (
        "Check that Resources are not circularly dependent by DependsOn, Ref, Sub, or"
        " GetAtt"
    )
    source_url = "https://github.com/aws-cloudformation/cfn-lint"
    tags = ["resources", "circularly", "dependson", "ref", "sub", "getatt"]

    def match(self, cfn: Template) -> RuleMatches:
        matches = []

        if cfn.graph is None:
            return []
        for cycle in cfn.graph.get_cycles(cfn):
            source, target = cycle[:2]
            if (
                cfn.graph.graph.nodes[source].get("type") == "Resource"
                and cfn.graph.graph.nodes[target].get("type") == "Resource"
            ):
                message = (
                    f"Circular Dependencies for resource {source}. Circular dependency"
                    f" with [{target}]"
                )
                path = ["Resources", source]
                matches.append(RuleMatch(path, message))

        return matches
