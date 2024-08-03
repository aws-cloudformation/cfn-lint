"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from typing import Any

from cfnlint.data.schemas.other import resources
from cfnlint.helpers import load_resource
from cfnlint.jsonschema import Validator
from cfnlint.rules import CloudFormationLintRule


class Tagging(CloudFormationLintRule):
    id = "E3024"
    shortdesc = "Validate tag configuration"
    description = (
        "Validates tag values to make sure they have unique keys "
        "and they follow pattern requirements"
    )
    source_url = "https://docs.aws.amazon.com/tag-editor/latest/userguide/tagging.html"
    tags = ["parameters", "resources", "tags"]

    def __init__(self) -> None:
        super().__init__()
        self._schema = load_resource(resources, "tagging.json")

    def tagging(self, validator: Validator, t: Any, instance: Any, schema: Any):
        if not t.get("taggable"):
            return

        validator = validator.evolve(
            function_filter=validator.function_filter.evolve(
                add_cfn_lint_keyword=False,
            ),
        )

        for err in validator.descend(
            instance=instance,
            schema=self._schema,
        ):
            err.validator = "tagging"
            yield err
