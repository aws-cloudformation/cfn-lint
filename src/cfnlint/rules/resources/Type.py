"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from collections import deque
from typing import Any, Dict

from cfnlint.jsonschema import ValidationError, Validator
from cfnlint.rules.jsonschema.Base import BaseJsonSchema
from cfnlint.schema.manager import PROVIDER_SCHEMA_MANAGER


class Type(BaseJsonSchema):
    """Check Base Resource Configuration"""

    id = "E3011"
    shortdesc = "Validate the CloudFormation resource type"
    description = "Resource types are validated against the spec accounting for regions"
    source_url = "https://github.com/aws-cloudformation/cfn-python-lint"
    tags = ["resources"]

    # pylint: disable=unused-argument
    def cfnresourcetype(
        self,
        validator: Validator,
        resource_type: str,
        instance: Any,
        schema: Dict[str, Any],
    ):
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
                    f"Resource type `{resource_type}` does not exist in '{region}'",
                    path=deque(["Type"]),
                    rule=self,
                )
