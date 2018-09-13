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


class AtLeastOne(CloudFormationLintRule):
    """Check Properties Resource Configuration"""
    id = 'E2522'
    shortdesc = 'Check Properties that need at least one of a list of properties'
    description = 'Making sure CloudFormation properties ' + \
                  'that require at least one property from a list. ' + \
                  'More than one can be included.'
    source_url = 'https://github.com/awslabs/cfn-python-lint'
    tags = ['resources']

    def __init__(self):
        """Init"""
        atleastonespec = cfnlint.helpers.load_resources('data/AdditionalSpecs/AtLeastOne.json')
        self.resource_types_specs = atleastonespec['ResourceTypes']
        self.property_types_specs = atleastonespec['PropertyTypes']
        for resource_type_spec in self.resource_types_specs:
            self.resource_property_types.append(resource_type_spec)
        for property_type_spec in self.property_types_specs:
            self.resource_sub_property_types.append(property_type_spec)

    def check(self, properties, atleastoneprops, path):
        """Check itself"""
        matches = []
        for atleastoneprop in atleastoneprops:
            count = 0
            for prop in atleastoneprop:
                if prop in properties:
                    count += 1

            if count == 0:
                message = 'At least one of [{0}] should be specified for {1}'
                matches.append(RuleMatch(
                    path,
                    message.format(', '.join(map(str, atleastoneprop)), '/'.join(map(str, path)))
                ))

        return matches

    def match_resource_sub_properties(self, properties, property_type, path, _):
        """Match for sub properties"""
        matches = []

        atleastoneprops = self.property_types_specs.get(property_type, {})
        matches.extend(self.check(properties, atleastoneprops, path))

        return matches

    def match_resource_properties(self, properties, resource_type, path, _):
        """Check CloudFormation Properties"""
        matches = []

        atleastoneprops = self.resource_types_specs.get(resource_type, {})
        matches.extend(self.check(properties, atleastoneprops, path))

        return matches
