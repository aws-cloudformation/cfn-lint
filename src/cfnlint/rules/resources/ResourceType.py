"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque
from typing import Any

from cfnlint.jsonschema import ValidationError, Validator
from cfnlint.rules.jsonschema.CfnLintKeyword import CfnLintKeyword
from cfnlint.schema.manager import PROVIDER_SCHEMA_MANAGER


class ResourceType(CfnLintKeyword):
    """Check Base Resource Configuration"""

    id = "E3006"
    shortdesc = "Validate the CloudFormation resource type"
    description = "Resource types are validated against the spec accounting for regions"
    source_url = "https://github.com/aws-cloudformation/cfn-lint"
    tags = ["resources"]

    def __init__(self) -> None:
        super().__init__(
            keywords=[
                "Resources/*",
            ],
        )

    def validate(self, validator: Validator, keywords: Any, instance: Any, schema: Any):
        resource_type = instance.get("Type")
        if not validator.is_type(resource_type, "string"):
            return

        resource_condition = instance.get("Condition")

        for region in validator.context.regions:
            if validator.is_type(resource_condition, "string"):
                if validator.cfn is None:
                    continue
                if False in validator.cfn.conditions.build_scenerios_on_region(
                    resource_condition, region
                ):
                    continue
            if resource_type in PROVIDER_SCHEMA_MANAGER.get_resource_types(
                region=region
            ):
                continue
            if not resource_type.startswith(
                ("Custom::", "AWS::Serverless::")
            ) and not resource_type.endswith("::MODULE"):
                yield ValidationError(
                    f"Resource type {resource_type!r} does not exist in {region!r}",
                    path=deque(["Type"]),
                    rule=self,
                )
