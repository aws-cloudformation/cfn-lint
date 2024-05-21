"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.helpers import valid_snapshot_types
from cfnlint.jsonschema import Validator
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema


class UpdateReplacePolicy(CfnLintJsonSchema):
    """Check Base Resource Configuration"""

    id = "E3036"
    shortdesc = "Check UpdateReplacePolicy values for Resources"
    description = "Check that the UpdateReplacePolicy values are valid"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-attribute-updatereplacepolicy.html"
    tags = ["resources", "updatereplacepolicy"]

    def __init__(self) -> None:
        super().__init__(
            keywords=["Resources/*/UpdateReplacePolicy"],
            all_matches=True,
        )

    def validate(self, validator: Validator, dP: str, instance, schema):
        enum = ["Delete", "Retain"]
        resource_name = validator.context.path.path[1]
        if (
            isinstance(resource_name, str)
            and validator.context.resources[resource_name].type in valid_snapshot_types
        ):
            enum.append("Snapshot")

        validator = validator.evolve(
            context=validator.context.evolve(
                functions=[
                    "Fn::Sub",
                    "Fn::Select",
                    "Fn::FindInMap",
                    "Fn::If",
                    "Ref",
                ]
            ),
            schema={"type": "string", "enum": enum},
        )

        yield from self._iter_errors(validator, instance)
