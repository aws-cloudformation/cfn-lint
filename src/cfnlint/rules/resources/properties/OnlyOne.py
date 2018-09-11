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


class OnlyOne(CloudFormationLintRule):
    """Check Properties Resource Configuration"""
    id = 'E2523'
    shortdesc = 'Check Properties that need only one of a list of properties'
    description = 'Making sure CloudFormation properties ' + \
                  'that require only one property from a list. ' + \
                  'One has to be specified.'
    source_url = 'https://github.com/awslabs/cfn-python-lint'
    tags = ['resources']

    def __init__(self):
        """Init"""
        onlyonespec = cfnlint.helpers.load_resources('data/AdditionalSpecs/OnlyOne.json')
        self.resource_types_specs = onlyonespec['ResourceTypes']
        self.property_types_specs = onlyonespec['PropertyTypes']
        for resource_type_spec in self.resource_types_specs:
            self.resource_property_types.append(resource_type_spec)
        for property_type_spec in self.property_types_specs:
            self.resource_sub_property_types.append(property_type_spec)

    def check(self, properties, onlyoneprops, path, cfn):
        """Check itself"""
        matches = []
        property_sets = cfn.get_values({'Properties': properties}, 'Properties', path)
        for property_set in property_sets:
            for onlyoneprop in onlyoneprops:
                count = 0
                for prop in onlyoneprop:
                    if prop in property_set['Value']:
                        count += 1

                if count != 1:
                    message = 'Only one of [{0}] should be specified for {1}'
                    matches.append(RuleMatch(
                        property_set['Path'],
                        message.format(', '.join(map(str, onlyoneprop)), '/'.join(map(str, property_set['Path'])))
                    ))

        return matches

    def match_resource_sub_properties(self, properties, property_type, path, cfn):
        """Match for sub properties"""
        matches = []

        onlyoneprops = self.property_types_specs.get(property_type, {})
        matches.extend(self.check(properties, onlyoneprops, path, cfn))

        return matches

    def match_resource_properties(self, properties, resource_type, path, cfn):
        """Check CloudFormation Properties"""
        matches = []

        onlyoneprops = self.resource_types_specs.get(resource_type, {})
        matches.extend(self.check(properties, onlyoneprops, path, cfn))

        return matches
