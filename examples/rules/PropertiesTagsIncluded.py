"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules import CloudFormationLintRule, RuleMatch
from cfnlint.schema import PROVIDER_SCHEMA_MANAGER


class PropertiesTagsIncluded(CloudFormationLintRule):
    """Check if Tags are included on supported resources"""

    id = "E9001"
    shortdesc = "Tags are included on resources that support it"
    description = "Check Tags for resources"
    tags = ["resources", "tags"]

    def match(self, cfn):
        """Check Tags for required keys"""

        matches = []

        all_tags = cfn.search_deep_keys("Tags")
        all_tags = [x for x in all_tags if x[0] == "Resources"]
        resources = cfn.get_resources()
        for resource_name, resource_obj in resources.items():
            resource_type = resource_obj.get("Type", "")
            resource_properties = resource_obj.get("Properties", {})
            if any(
                "Tags" in schema.schema["properties"]
                for (
                    _region,
                    schema,
                ) in PROVIDER_SCHEMA_MANAGER.get_resource_schemas_by_regions(
                    resource_type, cfn.regions
                )
            ):
                if "Tags" not in resource_properties:
                    message = "Missing Tags Properties for {0}"
                    matches.append(
                        RuleMatch(
                            ["Resources", resource_name, "Properties"],
                            message.format(
                                "/".join(
                                    map(str, ["Resources", resource_name, "Properties"])
                                )
                            ),
                        )
                    )

        return matches
