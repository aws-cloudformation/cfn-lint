"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any

from cfnlint.context import sam_generated_resources
from cfnlint.rules.jsonschema.MaxProperties import MaxProperties as ParentMaxProperties

# Base post-transform count per serverless resource type.
_SERVERLESS_BASE_RESOURCE_COUNTS = {
    # AWS::Serverless::Connector only adds permissions to existing resources,
    # it creates no standalone resource of its own.
    "AWS::Serverless::Connector": 0,
}
_DEFAULT_SERVERLESS_BASE_COUNT = 1


def post_sam_transform_resource_count(resources: dict[str, Any]) -> int:
    """Lower bound on the resource count after the SAM transform runs.

    Every written resource counts once, except ``AWS::Serverless::*``
    resources, which the transform replaces with the CloudFormation resources
    they expand to, plus every resource the transform generates on top of them
    (see ``sam_generated_resources``).
    """
    count = 0
    for resource in resources.values():
        if not isinstance(resource, dict):
            count += 1
            continue
        resource_type = resource.get("Type")
        if isinstance(resource_type, str) and resource_type.startswith(
            "AWS::Serverless::"
        ):
            count += _SERVERLESS_BASE_RESOURCE_COUNTS.get(
                resource_type, _DEFAULT_SERVERLESS_BASE_COUNT
            )
            continue
        count += 1

    seen = set(resources)
    for logical_id, _ in sam_generated_resources(resources):
        if logical_id not in seen:
            seen.add(logical_id)
            count += 1

    return count


class MaxProperties(ParentMaxProperties):
    """Check if maximum Resource limit is exceeded"""

    id = "E3010"
    shortdesc = "Resource limit not exceeded"
    description = (
        "Check the number of Resources in the template is less than the upper limit"
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cloudformation-limits.html"
    tags = ["resources", "limits"]

    def __init__(self) -> None:
        super().__init__("I3010")

    def _over_limit_message(self, validator, instance, mP) -> str:
        count = self._count_properties(validator, instance)
        return (
            f"{validator.context.path.path_string!r} "
            f"has {count} properties, more than the limit of {mP!r}"
        )

    def _count_properties(self, validator, instance) -> int:
        cfn = getattr(validator, "cfn", None)
        if (
            isinstance(instance, dict)
            and cfn is not None
            and cfn.has_serverless_transform()
        ):
            # The SAM transform no longer runs (#4491), so count the resources
            # CloudFormation will see after it runs instead of the written ones.
            return post_sam_transform_resource_count(instance)
        return len(instance)
