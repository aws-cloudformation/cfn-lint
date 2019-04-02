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
import datetime
import json
import re
import six
import cfnlint.helpers
from cfnlint import CloudFormationLintRule
from cfnlint import RuleMatch
from cfnlint.helpers import RESOURCE_SPECS


class JsonSize(CloudFormationLintRule):
    """Check if JSON Object Size is within the specified length"""
    id = 'E3502'
    shortdesc = 'Check if a JSON Object is within size limits'
    description = 'Validate properties that are JSON values so that their length is within the limits'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cloudformation-limits.html'
    tags = ['resources', 'limits', 'json']

    def initialize(self, cfn):
        """Initialize the rule"""
        for resource_type_spec in RESOURCE_SPECS.get(cfn.regions[0]).get('ResourceTypes'):
            self.resource_property_types.append(resource_type_spec)
        for property_type_spec in RESOURCE_SPECS.get(cfn.regions[0]).get('PropertyTypes'):
            self.resource_sub_property_types.append(property_type_spec)

    def _serialize_date(self, obj):
        if isinstance(obj, datetime.date):
            return obj.isoformat()
        raise TypeError('Object of type {} is not JSON serializable'.format(obj.__class__.__name__))

    def check_value(self, value, path, prop, cfn, specs):
        """Check Role.AssumeRolePolicyDocument is within limits"""
        matches = []

        def remove_functions(obj):
            """ Replaces intrinsic functions with string """
            if isinstance(obj, dict):
                new_obj = {}
                if len(obj) == 1:
                    for k, v in obj.items():
                        if k in cfnlint.helpers.FUNCTIONS:
                            if k == 'Fn::Sub':
                                if isinstance(v, six.string_types):
                                    return re.sub(r'\${.*}', '', v)
                                if isinstance(v, list):
                                    return re.sub(r'\${.*}', '', v[0])
                        else:
                            new_obj[k] = remove_functions(v)
                            return new_obj
                else:
                    for k, v in obj.items():
                        new_obj[k] = remove_functions(v)
                    return new_obj
            elif isinstance(obj, list):
                new_list = []
                for v in obj:
                    new_list.append(remove_functions(v))
                return new_list

            return obj

        scenarios = cfn.get_object_without_nested_conditions(value, path)
        json_max_size = specs.get('JsonMax')
        for scenario in scenarios:
            if len(json.dumps(remove_functions(scenario['Object']), default=self._serialize_date)) > json_max_size:
                if scenario['Scenario']:
                    message = 'Role trust policy JSON text cannot be longer than {0} characters when {1}'
                    scenario_text = ' and '.join(['when condition "%s" is %s' % (k, v) for (k, v) in scenario['Scenario'].items()])
                    matches.append(RuleMatch(path + [prop], message.format(json_max_size, scenario_text)))
                else:
                    message = 'Role trust policy JSON text cannot be longer than {0} characters'
                    matches.append(
                        RuleMatch(
                            path + [prop],
                            message.format(json_max_size),
                        )
                    )

        return matches

    def check(self, cfn, properties, specs, path):
        """Check itself"""
        matches = []
        for p_value, p_path in properties.items_safe(path[:]):
            for prop in p_value:
                if prop in specs:
                    value = specs.get(prop).get('Value', {})
                    if value:
                        value_type = value.get('ValueType', '')
                        primitive_type = specs.get(prop).get('PrimitiveType')
                        if primitive_type == 'Json':
                            matches.extend(
                                self.check_value(
                                    p_value, p_path, prop, cfn,
                                    RESOURCE_SPECS.get(cfn.regions[0]).get('ValueTypes').get(value_type, {})
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
