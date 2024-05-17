"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from typing import Any

from cfnlint.jsonschema import ValidationError, Validator
from cfnlint.rules.jsonschema.CfnLintKeyword import CfnLintKeyword


class DependsOn(CfnLintKeyword):
    """Check Base Resource Configuration"""

    id = "E3005"
    shortdesc = "Check DependsOn values for Resources"
    description = "Check that the DependsOn values are valid"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-attribute-dependson.html"
    tags = ["resources", "dependson"]

    def __init__(self):
        super().__init__(keywords=["Resources/*/DependsOn", "Resources/*/DependsOn/*"])

    def validate(self, validator: Validator, s: Any, instance: Any, schema: Any):
        if not validator.is_type(instance, "string"):
            return

        resources = list(validator.context.resources.keys())

        if len(validator.context.path.path) > 1:
            if (
                isinstance(validator.context.path.path[1], str)
                and validator.context.path.path[1] in resources
            ):
                resources.remove(validator.context.path.path[1])

        if instance not in resources:
            yield ValidationError(
                f"{instance!r} is not one of {resources!r}",
            )
            return

        if not validator.cfn:
            return

        for scenario in validator.cfn.is_resource_available(
            list(validator.context.path.path), instance
        ):
            if scenario:
                scenario_text = " and ".join(
                    [
                        f"when condition {k!r} is {scenario[k]!r}"
                        for k in sorted(scenario)
                    ]
                )

                yield ValidationError(f"{instance!r} will not exist {scenario_text}")
