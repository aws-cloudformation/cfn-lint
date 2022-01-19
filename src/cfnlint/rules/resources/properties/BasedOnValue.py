"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import re
from cfnlint.rules import CloudFormationLintRule
import cfnlint.helpers
from cfnlint.data import AdditionalSpecs
from cfnlint.rules import RuleMatch


class BasedOnValue(CloudFormationLintRule):
    """Generic rule for checking properties based on value"""
    spec_type = ''
    message = ''

    def __init__(self):
        super(BasedOnValue, self).__init__()
        basedonvalue = cfnlint.helpers.load_resource(
            AdditionalSpecs, 'BasedOnValue.json')
        self.resource_types_specs = basedonvalue['ResourceTypes']
        self.property_types_specs = basedonvalue['PropertyTypes']
        for resource_type, resource_specs in self.resource_types_specs.items():
            for based_on_specs in resource_specs.values():
                for spec in based_on_specs:
                    if spec.get(self.spec_type):
                        self.resource_property_types.append(resource_type)
        for resource_type, resource_specs in self.property_types_specs.items():
            for based_on_specs in resource_specs.values():
                for spec in based_on_specs:
                    if spec.get(self.spec_type):
                        self.resource_sub_property_types.append(resource_type)

    def _check_value(self, value, spec, cfn):
        """ Checks a value to see if it fits in the spec """
        if isinstance(value, str):
            regex = spec.get('Regex')
            if regex:
                if re.match(spec.get('Regex'), value):
                    return True
        elif isinstance(value, dict):
            if len(value) == 1:
                for k, v in value.items():
                    ref = spec.get('Ref')
                    if ref:
                        if k == 'Ref':
                            if isinstance(v, str):
                                return cfn.template.get('Resources').get(v, {}).get('Type') in ref

                    getatt = spec.get('GetAtt')
                    if getatt:
                        if k == 'Fn::GetAtt':
                            if isinstance(v, list):
                                restype = cfn.template.get('Resources').get(v[0]).get('Type')
                                if restype in getatt:
                                    return getatt.get(restype) == v[1]

        return False

    #pylint: disable=unused-argument
    def _check_prop(self, prop, scenario):
        return False

    def _check_obj(self, properties, specs, path, cfn):
        matches = []
        for k, v in specs.items():
            for s in v:
                spec_values = s.get(self.spec_type)
                if spec_values:
                    property_set = [k] + spec_values
                    scenarios = cfn.get_object_without_conditions(
                        properties, property_names=property_set)
                    for scenario in scenarios:
                        if self._check_value(scenario.get('Object').get(k), s, cfn):
                            for property_name in spec_values:
                                if self._check_prop(property_name, scenario):
                                    if scenario['Scenario'] is None:
                                        message = 'When property \'{0}\' has its current value property \'{1}\' {2} at {3}'
                                        matches.append(RuleMatch(
                                            path,
                                            message.format(k, property_name,
                                                           self.message, '/'.join(map(str, path)))
                                        ))
                                    else:
                                        scenario_text = ' and '.join(['when condition "%s" is %s' % (
                                            k, v) for (k, v) in scenario['Scenario'].items()])
                                        message = 'When property \'{0}\' has its current value property \'{1}\' {2} when {3}'
                                        matches.append(RuleMatch(
                                            path,
                                            message.format(k, property_name, self.message, scenario_text)))

        return matches

    def match_resource_properties(self, properties, resource_type, path, cfn):
        """Check CloudFormation Properties"""
        matches = []

        if properties is None:
            # covered under rule E3001.  If there are required properties properties is required first
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
            # covered under rule E3001.  If there are required properties properties is required first
            return matches

        # Need to get this spec
        specs = self.property_types_specs.get(property_type)

        matches.extend(
            self._check_obj(properties, specs, path, cfn)
        )

        return matches
