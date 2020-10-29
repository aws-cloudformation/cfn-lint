"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import re
import six
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch
import cfnlint.helpers
from cfnlint.data import AdditionalSpecs


class UnwantedBasedOnValue(CloudFormationLintRule):
    """Check Unwanted Properties are supplied when another property has a certain value"""
    id = 'E3018'
    shortdesc = 'Property is unwanted based on another properties value'
    description = 'When certain properties have a certain value it results in other properties not being needed. ' \
        'This rule will validate those unwanted properties are not specified when those values are supplied'
    tags = ['resources']

    def __init__(self):
        """Init"""
        super(UnwantedBasedOnValue, self).__init__()
        unwantedbasedonvalue = cfnlint.helpers.load_resource(
            AdditionalSpecs, 'UnwantedBasedOnValue.json')
        self.resource_types_specs = unwantedbasedonvalue['ResourceTypes']
        self.property_types_specs = unwantedbasedonvalue['PropertyTypes']
        for resource_type_spec in self.resource_types_specs:
            self.resource_property_types.append(resource_type_spec)
        for property_type_spec in self.property_types_specs:
            self.resource_sub_property_types.append(property_type_spec)

    def _check_value(self, value, spec, cfn):
        """ Checks a value to see if it fits in the spec """
        if isinstance(value, six.string_types):
            regex = spec.get('Regex')
            if regex:
                if re.match(spec.get('Regex'), value):
                    return True
        if isinstance(value, dict):
            if len(value) == 1:
                for k, v in value.items():
                    ref = spec.get('Ref')
                    if ref:
                        if k == 'Ref':
                            if isinstance(v, six.string_types):
                                return cfn.template.get('Resources').get(v, {}).get('Type') in ref

                    getatt = spec.get('GetAtt')
                    if getatt:
                        if k == 'Fn::GetAtt':
                            if isinstance(v, list):
                                restype = cfn.template.get('Resources').get(v[0]).get('Type')
                                if restype in getatt:
                                    return getatt.get(restype) == v[1]

        return False

    def _check_obj(self, properties, specs, path, cfn):
        matches = []
        for k, v in specs.items():
            for s in v:
                unwanted_props = [k] + s.get('UnwantedProperties')
                scenarios = cfn.get_object_without_conditions(
                    properties, property_names=unwanted_props)
                for scenario in scenarios:
                    if self._check_value(scenario.get('Object').get(k), s, cfn):
                        for unwanted_prop in s.get('UnwantedProperties'):
                            if unwanted_prop in scenario.get('Object'):
                                if scenario['Scenario'] is None:
                                    message = 'When property \'{0}\' has its current value property \'{1}\' should not be specified at {2}'
                                    matches.append(RuleMatch(
                                        path,
                                        message.format(k, unwanted_prop, '/'.join(map(str, path)))
                                    ))
                                else:
                                    scenario_text = ' and '.join(['when condition "%s" is %s' % (
                                        k, v) for (k, v) in scenario['Scenario'].items()])
                                    message = 'When property \'{0}\' has its current value property \'{1}\' should not be specified when {2}'
                                    matches.append(RuleMatch(
                                        path,
                                        message.format(k, unwanted_prop, scenario_text)))

        return matches

    def match_resource_properties(self, properties, resource_type, path, cfn):
        """Check CloudFormation Properties"""
        matches = []

        if properties is None:
            # covered under rule E3001.  If there are unwanted properties properties is unwanted first
            return matches

        # Need to get this spec
        specs = self.resource_types_specs.get(resource_type)

        matches.extend(
            self._check_obj(properties, specs, path, cfn)
        )

        return matches

    def match_resource_sub_properties(self, properties, property_type, path, cfn):
        """Check CloudFormation Properties"""
        matches = []

        if properties is None:
            # covered under rule E3001.  If there are unwanted properties properties is unwanted first
            return matches

        # Need to get this spec
        specs = self.property_types_specs.get(property_type)

        matches.extend(
            self._check_obj(properties, specs, path, cfn)
        )

        return matches
