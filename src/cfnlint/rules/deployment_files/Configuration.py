"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from cfnlint._typing import Any, RuleMatches
from cfnlint.jsonschema import StandardValidator
from cfnlint.rules.jsonschema.Base import BaseJsonSchema


class Configuration(BaseJsonSchema):

    id = "E0100"
    shortdesc = "Validate deployment file configuration"
    description = (
        "Validate if a deployment file has the correct syntax "
        "for one of the supported formats"
    )
    source_url = "https://github.com/aws-cloudformation/cfn-lint"
    tags = ["base"]

    def validate_deployment_file(
        self, data: dict[str, Any], schema: dict[str, Any]
    ) -> RuleMatches:
        matches = []

        validator = StandardValidator(schema)

        matches.extend(self.json_schema_validate(validator, data, []))

        return matches
