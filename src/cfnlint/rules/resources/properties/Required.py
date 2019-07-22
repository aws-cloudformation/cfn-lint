"""
  Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.

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
from cfnlint.helpers import RESOURCE_SPECS


class Required(CloudFormationLintRule):
    """ Check for required properties """
    id = 'E3003'
    shortdesc = 'Required Resource Parameters are missing'
    description = 'Making sure that Resources properties ' + \
                  'that are required exist'
    source_url = 'https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/cfn-resource-specification.md#required'
    tags = ['resources']

    def __init__(self):
        """Init"""
        super(Required, self).__init__()
        self.custom_spec = {}

    def initialize(self, cfn):
        """Initialize the rule"""
        for resource_type_spec in RESOURCE_SPECS.get(
                cfn.regions[0]).get('ResourceTypes'):
            self.resource_property_types.append(resource_type_spec)
            if resource_type_spec == 'AWS::CloudFormation::CustomResource':
                self.custom_spec = RESOURCE_SPECS.get(
                    cfn.regions[0]).get('ResourceTypes').get(
                        'AWS::CloudFormation::CustomResource').get(
                            'Properties', {})
        for property_type_spec in RESOURCE_SPECS.get(
                cfn.regions[0]).get('PropertyTypes'):
            self.resource_sub_property_types.append(property_type_spec)

    def custom_check(self, text, path):
        """ Check Custom Property """
        matches = []

        if not isinstance(text, dict):
            # Covered with Properties not with Required
            return matches

        # Return empty matches if we run into a function that is being used to get an object
        # Selects could be used to return an object when used with a FindInMap
        if text.is_function_returning_object():
            return matches

        for keys, k_path in text.keys_safe(path):
            for prop in self.custom_spec:
                if self.custom_spec[prop]['Required']:
                    if prop not in keys:
                        message = 'Property {0} missing at {1}'
                        matches.append(RuleMatch(k_path, message.format(
                            prop, '/'.join(map(str, k_path)))))
        return matches

    def check(self, properties, resourcespec, path):
        """ Check for required properties """
        matches = []

        if not isinstance(properties, dict):
            # Covered with Properties not with Required
            return matches

        # Return empty matches if we run into a function that is being used to get an object
        # Selects could be used to return an object when used with a FindInMap
        if properties.is_function_returning_object():
            return matches

        for keys, k_path in properties.keys_safe(path[:]):
            for prop in resourcespec:
                if resourcespec[prop]['Required']:
                    if prop not in keys:
                        message = 'Property {0} missing at {1}'
                        matches.append(RuleMatch(k_path, message.format(
                            prop, '/'.join(map(str, k_path)))))

        return matches

    def match(self, cfn):
        """Check CloudFormation Properties"""
        matches = []

        for resourcename, resourcevalue in cfn.get_resources().items():
            if 'Properties' in resourcevalue and 'Type' in resourcevalue:
                resourcetype = resourcevalue['Type']
                if resourcetype.startswith('Custom::') and resourcetype not in self.resource_property_types:
                    resourcetype = 'AWS::CloudFormation::CustomResource'
                    path = ['Resources', resourcename, 'Properties']
                    matches.extend(self.custom_check(resourcevalue['Properties'], path))

        return matches

    def match_resource_sub_properties(
            self, properties, property_type, path, cfn):
        """Match for sub properties"""
        matches = list()

        specs = RESOURCE_SPECS.get(cfn.regions[0]).get(
            'PropertyTypes').get(property_type, {}).get('Properties', {})
        matches.extend(self.check(properties, specs, path))

        return matches

    def match_resource_properties(self, properties, resource_type, path, cfn):
        """Check CloudFormation Properties"""
        matches = list()

        specs = RESOURCE_SPECS.get(cfn.regions[0]).get(
            'ResourceTypes').get(resource_type, {}).get('Properties', {})
        matches.extend(self.check(properties, specs, path))

        return matches
