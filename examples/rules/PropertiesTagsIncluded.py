"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch
import cfnlint.helpers


class PropertiesTagsIncluded(CloudFormationLintRule):
    """Check if Tags are included on supported resources"""
    id = 'E9001'
    shortdesc = 'Tags are included on resources that support it'
    description = 'Check Tags for resources'
    tags = ['resources', 'tags']

    def get_resources_with_tags(self, region):
        """Get resource types that support tags"""
        resourcespecs = cfnlint.helpers.RESOURCE_SPECS[region]
        resourcetypes = resourcespecs['ResourceTypes']

        matches = []
        for resourcetype, resourceobj in resourcetypes.items():
            propertiesobj = resourceobj.get('Properties')
            if propertiesobj:
                if 'Tags' in propertiesobj:
                    matches.append(resourcetype)

        return matches

    def match(self, cfn):
        """Check Tags for required keys"""

        matches = []

        all_tags = cfn.search_deep_keys('Tags')
        all_tags = [x for x in all_tags if x[0] == 'Resources']
        resources_tags = self.get_resources_with_tags(cfn.regions[0])
        resources = cfn.get_resources()
        for resource_name, resource_obj in resources.items():
            resource_type = resource_obj.get('Type', "")
            resource_properties = resource_obj.get('Properties', {})
            if resource_type in resources_tags:
                if 'Tags' not in resource_properties:
                    message = "Missing Tags Properties for {0}"
                    matches.append(
                        RuleMatch(
                            ['Resources', resource_name, 'Properties'],
                            message.format('/'.join(map(str, ['Resources', resource_name, 'Properties'])))))

        return matches
