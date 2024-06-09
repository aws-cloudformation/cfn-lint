"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from typing import Any

from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules.jsonschema import CfnLintKeyword


class DependsOnObsolete(CfnLintKeyword):
    """Check unneeded DepensOn Resource Configuration"""

    id = "W3005"
    shortdesc = "Check obsolete DependsOn configuration for Resources"
    description = (
        "Check if DependsOn is specified if not needed. "
        "A Ref or a Fn::GetAtt already is an implicit dependency."
    )
    source_url = (
        "https://aws.amazon.com/blogs/devops/optimize-aws-cloudformation-templates/"
    )
    tags = ["resources", "dependson", "ref", "getatt"]

    def __init__(self) -> None:
        super().__init__(keywords=["Resources/*/DependsOn", "Resources/*/DependsOn/*"])

    def validate(
        self, validator: Validator, s: Any, instance: Any, schema: Any
    ) -> ValidationResult:
        if not validator.is_type(instance, "string"):
            return

        from_resource_name = validator.context.path.path[1]
        if validator.cfn.graph is None:
            return
        edges = validator.cfn.graph.graph.get_edge_data(from_resource_name, instance)
        # returns None if no edge exists
        if not edges:
            return
        for _, edge in edges.items():
            if edge["label"] != "DependsOn":
                path = list(validator.context.path.path)[0:2] + edge["source_paths"]
                yield ValidationError(
                    f"{instance!r} dependency already enforced"
                    f" by a {edge['label']!r} at {'/'.join(str(e) for e in path)!r}",
                )
