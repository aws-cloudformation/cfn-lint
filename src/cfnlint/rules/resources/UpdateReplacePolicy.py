"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.helpers import valid_snapshot_types
from cfnlint.jsonschema import Validator
from cfnlint.rules import CloudFormationLintRule


class UpdateReplacePolicy(CloudFormationLintRule):
    """Check Base Resource Configuration"""

    id = "E3036"
    shortdesc = "Check UpdateReplacePolicy values for Resources"
    description = "Check that the UpdateReplacePolicy values are valid"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-attribute-updatereplacepolicy.html"
    tags = ["resources", "updatereplacepolicy"]

    # pylint: disable=unused-argument, arguments-renamed
    def updatereplacepolicy(self, validator: Validator, uRp: str, instance, schema):
        validator = validator.evolve(
            context=validator.context.evolve(
                functions=[
                    "Fn::Sub",
                    "Fn::Select",
                    "Fn::FindInMap",
                    "Fn::If",
                    "Ref",
                ]
            )
        )
        enum = ["Delete", "Retain"]
        if (
            validator.context.resources[validator.context.path[1]].type
            in valid_snapshot_types
        ):
            enum.append("Snapshot")

        for err in validator.descend(instance, {"type": "string", "enum": enum}):
            err.rule = self
            yield err
