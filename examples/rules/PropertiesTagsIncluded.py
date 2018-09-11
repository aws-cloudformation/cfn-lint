"""
  Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.

  Permission is hereby granted, free of charge, to any person obtaining a copy of this
  software and associated documentation files (the "Software"), to deal in the Software
  without restriction, including without limitation the rights to use, copy, modify,
  merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
  permit persons to whom the Software is furnished to do so.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
  INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
  PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
  HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
  OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
  SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
from cfnlint import CloudFormationLintRule
from cfnlint import RuleMatch
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
