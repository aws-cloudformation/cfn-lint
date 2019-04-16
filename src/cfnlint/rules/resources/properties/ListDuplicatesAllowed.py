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
import hashlib
import json
from cfnlint import CloudFormationLintRule
from cfnlint import RuleMatch

from cfnlint.helpers import RESOURCE_SPECS


class ListDuplicatesAllowed(CloudFormationLintRule):
    """Check if duplicates exist in a List"""
    id = 'I3037'
    shortdesc = 'Check if a list that allows duplicates has any duplicates'
    description = 'Certain lists support duplicate items.' \
                  'Provide an alert when list of strings or numbers have repeats.'
    source_url = 'https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#rules-1'
    tags = ['resources', 'property', 'list']

    def initialize(self, cfn):
        """Initialize the rule"""
        for resource_type_spec in RESOURCE_SPECS.get(cfn.regions[0]).get('ResourceTypes'):
            self.resource_property_types.append(resource_type_spec)
        for property_type_spec in RESOURCE_SPECS.get(cfn.regions[0]).get('PropertyTypes'):
            self.resource_sub_property_types.append(property_type_spec)

    def _check_duplicates(self, values, path, scenario=None):
        """ Check for Duplicates """
        matches = []

        list_items = []
        if isinstance(values, list):
            for index, value in enumerate(values):
                value_hash = hashlib.sha1(json.dumps(value, sort_keys=True).encode('utf-8')).hexdigest()
                if value_hash in list_items:
                    if not scenario:
                        message = 'List has a duplicate value at {0}'
                        matches.append(RuleMatch(path + [index], message.format('/'.join(map(str, path + [index])))))
                    else:
                        scenario_text = ' and '.join(['condition "%s" is %s' % (k, v) for (k, v) in scenario.items()])
                        message = 'List has a duplicate value at {0} when {1}'
                        matches.append(RuleMatch(path, message.format('/'.join(map(str, path)), scenario_text)))

                list_items.append(value_hash)

        return matches

    def check_duplicates(self, values, path, cfn):
        """ Check for duplicates """
        matches = []

        if isinstance(values, list):
            matches.extend(self._check_duplicates(values, path))
        elif isinstance(values, dict):
            props = cfn.get_object_without_conditions(values)
            for prop in props:
                matches.extend(self._check_duplicates(prop.get('Object'), path, prop.get('Scenario')))

        return matches

    def check(self, cfn, properties, value_specs, path):
        """Check itself"""
        matches = list()
        for p_value, p_path in properties.items_safe(path[:]):
            for prop in p_value:
                if prop in value_specs:
                    property_type = value_specs.get(prop).get('Type')
                    primitive_type = value_specs.get(prop).get('PrimitiveItemType')
                    duplicates_allowed = value_specs.get(prop).get('DuplicatesAllowed', False)
                    if property_type == 'List' and duplicates_allowed and primitive_type in ['String', 'Integer']:
                        matches.extend(
                            self.check_duplicates(
                                p_value[prop], p_path + [prop], cfn
                            )
                        )

        return matches

    def match_resource_sub_properties(self, properties, property_type, path, cfn):
        """Match for sub properties"""
        matches = list()

        specs = RESOURCE_SPECS.get(cfn.regions[0]).get('PropertyTypes').get(property_type, {}).get('Properties', {})
        matches.extend(self.check(cfn, properties, specs, path))

        return matches

    def match_resource_properties(self, properties, resource_type, path, cfn):
        """Check CloudFormation Properties"""
        matches = list()

        specs = RESOURCE_SPECS.get(cfn.regions[0]).get('ResourceTypes').get(resource_type, {}).get('Properties', {})
        matches.extend(self.check(cfn, properties, specs, path))

        return matches
