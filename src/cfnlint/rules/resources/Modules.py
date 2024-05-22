"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint._typing import RuleMatches
from cfnlint.rules import CloudFormationLintRule, RuleMatch
from cfnlint.template import Template


class Modules(CloudFormationLintRule):
    """Check that Modules do not contain invalid data"""

    id = "E5001"
    shortdesc = "Check that Modules resources are valid"
    description = "Check that Modules resources are valid"
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/"
    tags = ["resources", "modules"]

    def match(self, cfn: Template) -> RuleMatches:
        matches = []
        resource_properties = cfn.get_resources()
        resource_dict = {
            key: resource_properties[key]
            for key in resource_properties
            if isinstance(resource_properties[key], dict)
        }
        for resource_name, resource_values in resource_dict.items():
            module = {
                "Type": v
                for (k, v) in resource_values.items()
                if str(v).endswith("::MODULE") is True
            }
            if module:
                matches.extend(self.check_metadata_keys(cfn))

                matches.extend(self.check_tags(resource_name, resource_values))

                matches.extend(
                    self.check_policy("CreationPolicy", resource_name, resource_values)
                )

                matches.extend(
                    self.check_policy("UpdatePolicy", resource_name, resource_values)
                )

        return matches

    def check_policy(self, policy, resource_name, resource_values):
        """Ensure invalid policies are not used"""
        matches = []
        if resource_values.get(policy, {}):
            path = ["Resources", resource_name, policy]
            matches.append(RuleMatch(path, f"{policy} is not permitted within Modules"))

        return matches

    def check_tags(self, resource_name, resource_values):
        """Ensure invalid policies are not used"""
        matches = []
        properties = resource_values.get("Properties", {})
        if properties.get("Tags"):
            path = ["Resources", resource_name, "Properties", "Tags"]
            matches.append(RuleMatch(path, "Tags is not permitted within Modules"))

        return matches

    def check_metadata_keys(self, cfn):
        """Ensure reserved metadata key AWS::CloudFormation::Module is not used"""
        modules = cfn.get_modules().keys()
        matches = []
        reserved_key = "AWS::CloudFormation::Module"
        refs = cfn.search_deep_keys(reserved_key)
        for ref in refs:
            if (ref[1] in modules) and (len(ref) > 3):
                if ref[0] == "Resources" and ref[2] == "Metadata":
                    matches.append(
                        RuleMatch(ref, f"The Metadata key {reserved_key} is reserved")
                    )
        return matches
