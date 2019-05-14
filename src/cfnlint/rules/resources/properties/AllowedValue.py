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


class AllowedValue(CloudFormationLintRule):
    """Check if properties have a valid value"""
    id = 'E3030'
    shortdesc = 'Check if properties have a valid value'
    description = 'Check if properties have a valid value in case of an enumator'
    source_url = 'https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/cfn-resource-specification.md#allowedvalue'
    tags = ['resources', 'property', 'allowed value']

    def initialize(self, cfn):
        """Initialize the rule"""
        for resource_type_spec in RESOURCE_SPECS.get(cfn.regions[0]).get('ResourceTypes'):
            self.resource_property_types.append(resource_type_spec)
        for property_type_spec in RESOURCE_SPECS.get(cfn.regions[0]).get('PropertyTypes'):
            self.resource_sub_property_types.append(property_type_spec)

    def check_value(self, value, path, property_name, **kwargs):
        """Check Value"""
        matches = []

        allowed_value_specs = kwargs.get('value_specs', {}).get('AllowedValues', {})

        if allowed_value_specs:

            # Ignore values with dynamic references. Simple check to prevent false-positives
            # See: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/dynamic-references.html
            if '{{resolve:' not in str(value):
                # Always compare the allowed value as a string, strict typing is not of concern for this rule
                if str(value) not in allowed_value_specs:
                    message = 'You must specify a valid value for {0} ({1}).\nValid values are {2}'
                    matches.append(RuleMatch(path, message.format(property_name, value, allowed_value_specs)))

        return matches

    def check(self, cfn, properties, value_specs, property_specs, path):
        """Check itself"""
        matches = list()
        for p_value, p_path in properties.items_safe(path[:]):
            for prop in p_value:
                if prop in value_specs:
                    value = value_specs.get(prop).get('Value', {})
                    if value:
                        value_type = value.get('ValueType', '')
                        property_type = property_specs.get('Properties').get(prop).get('Type')
                        matches.extend(
                            cfn.check_value(
                                p_value, prop, p_path,
                                check_value=self.check_value,
                                value_specs=RESOURCE_SPECS.get(cfn.regions[0]).get('ValueTypes').get(value_type, {}),
                                cfn=cfn, property_type=property_type, property_name=prop
                            )
                        )

        return matches

    def match_resource_sub_properties(self, properties, property_type, path, cfn):
        """Match for sub properties"""
        matches = list()

        specs = RESOURCE_SPECS.get(cfn.regions[0]).get('PropertyTypes').get(property_type, {}).get('Properties', {})
        property_specs = RESOURCE_SPECS.get(cfn.regions[0]).get('PropertyTypes').get(property_type)
        matches.extend(self.check(cfn, properties, specs, property_specs, path))

        return matches

    def match_resource_properties(self, properties, resource_type, path, cfn):
        """Check CloudFormation Properties"""
        matches = list()

        specs = RESOURCE_SPECS.get(cfn.regions[0]).get('ResourceTypes').get(resource_type, {}).get('Properties', {})
        resource_specs = RESOURCE_SPECS.get(cfn.regions[0]).get('ResourceTypes').get(resource_type)
        matches.extend(self.check(cfn, properties, specs, resource_specs, path))

        return matches
