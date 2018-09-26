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


class Inclusive(CloudFormationLintRule):
    """Check Properties Resource Configuration"""
    id = 'E2521'
    shortdesc = 'Check Properties that are required together'
    description = 'Make sure CloudFormation resource properties ' + \
                  'are included together when required'
    source_url = 'https://github.com/awslabs/cfn-python-lint'
    tags = ['resources']

    def __init__(self):
        """Init"""
        inclusivespec = cfnlint.helpers.load_resources('data/AdditionalSpecs/Inclusive.json')
        self.resource_types_specs = inclusivespec['ResourceTypes']
        self.property_types_specs = inclusivespec['PropertyTypes']
        for resource_type_spec in self.resource_types_specs:
            self.resource_property_types.append(resource_type_spec)
        for property_type_spec in self.property_types_specs:
            self.resource_sub_property_types.append(property_type_spec)

    def check(self, properties, inclusions, path):
        """Check itself"""
        matches = []
        # property_sets = cfn.get_values({'Properties': properties}, 'Properties', path)
        if not properties:
            return matches

        for items, p in properties.items_safe(path=path, type_t=(dict)):
            for k in items.keys():
                if k in inclusions:
                    for incl_property in inclusions[k]:
                        if incl_property not in items.keys():
                            message = 'Property {0} should exist with {1} for {2}'
                            matches.append(RuleMatch(
                                p,
                                message.format(incl_property, k, '/'.join(map(str, p)))
                            ))

        return matches

    def match_resource_sub_properties(self, properties, property_type, path, _):
        """Match for sub properties"""
        matches = []

        inclusions = self.property_types_specs.get(property_type, {})
        matches.extend(self.check(properties, inclusions, path))

        return matches

    def match_resource_properties(self, properties, resource_type, path, _):
        """Check CloudFormation Properties"""
        matches = []

        inclusions = self.resource_types_specs.get(resource_type, {})
        matches.extend(self.check(properties, inclusions, path))

        return matches
