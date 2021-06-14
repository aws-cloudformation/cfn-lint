"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import re
import six
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch

from cfnlint.helpers import RESOURCE_SPECS


class AllowedPattern(CloudFormationLintRule):
    """Check if parameters have a valid value"""
    id = 'W2031'
    shortdesc = 'Check if parameters have a valid value based on an allowed pattern'
    description = 'Check if parameters have a valid value in a pattern. The Parameter\'s allowed pattern is based on the usages in property (Ref)'
    source_url = 'https://github.com/aws-cloudformation/cfn-python-lint/blob/main/docs/cfn-resource-specification.md#allowedpattern'
    tags = ['parameters', 'resources', 'property', 'allowed pattern']

    def initialize(self, cfn):
        """Initialize the rule"""
        for resource_type_spec in RESOURCE_SPECS.get(cfn.regions[0]).get('ResourceTypes'):
            self.resource_property_types.append(resource_type_spec)
        for property_type_spec in RESOURCE_SPECS.get(cfn.regions[0]).get('PropertyTypes'):
            self.resource_sub_property_types.append(property_type_spec)

    def check_value_ref(self, value, path, **kwargs):
        """Check Ref"""
        matches = []

        cfn = kwargs.get('cfn')
        if 'Fn::If' in path:
            self.logger.debug(
                'Not able to guarentee that the default value hasn\'t been conditioned out')
            return matches
        if path[0] == 'Resources' and 'Condition' in cfn.template.get(
                path[0], {}).get(path[1]):
            self.logger.debug(
                'Not able to guarentee that the default value '
                'hasn\'t been conditioned out')
            return matches

        allowed_pattern = kwargs.get('value_specs', {}).get('AllowedPattern', {})
        allowed_pattern_regex = kwargs.get('value_specs', {}).get('AllowedPatternRegex', {})
        allowed_pattern_description = kwargs.get('value_specs', {}).get('AllowedPatternDescription', {})

        if allowed_pattern_regex:
            if value in cfn.template.get('Parameters', {}):
                param = cfn.template.get('Parameters').get(value, {})
                parameter_values = param.get('AllowedValues')
                default_value = param.get('Default')
                parameter_type = param.get('Type')
                if isinstance(parameter_type, six.string_types):
                    if ((not parameter_type.startswith('List<')) and
                            (not parameter_type.startswith('AWS::SSM::Parameter::Value<')) and
                            parameter_type not in ['CommaDelimitedList', 'List<String>']):
                        # Check Allowed Values
                        if parameter_values:
                            for index, allowed_value in enumerate(parameter_values):
                                if not re.match(allowed_pattern_regex, str(allowed_value)):
                                    param_path = ['Parameters', value, 'AllowedValues', index]
                                    description = allowed_pattern_description or 'Valid values must match pattern {0}'.format(allowed_pattern)
                                    message = 'You must specify a valid allowed value for {0} ({1}). {2}'
                                    matches.append(RuleMatch(param_path, message.format(
                                        value, allowed_value, description)))
                        if default_value:
                            # Check Default, only if no allowed Values are specified in the parameter (that's covered by E2015)
                            if not re.match(allowed_pattern_regex, str(default_value)):
                                param_path = ['Parameters', value, 'Default']
                                description = allowed_pattern_description or 'Valid values must match pattern {0}'.format(allowed_pattern)
                                message = 'You must specify a valid Default value for {0} ({1}). {2}'
                                matches.append(RuleMatch(param_path, message.format(
                                    value, default_value, description)))

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
                                check_ref=self.check_value_ref,
                                value_specs=RESOURCE_SPECS.get(cfn.regions[0]).get(
                                    'ValueTypes').get(value_type, {}),
                                cfn=cfn, property_type=property_type, property_name=prop
                            )
                        )

        return matches

    def match_resource_sub_properties(self, properties, property_type, path, cfn):
        """Match for sub properties"""
        matches = list()

        specs = RESOURCE_SPECS.get(cfn.regions[0]).get(
            'PropertyTypes').get(property_type, {}).get('Properties', {})
        property_specs = RESOURCE_SPECS.get(cfn.regions[0]).get('PropertyTypes').get(property_type)
        matches.extend(self.check(cfn, properties, specs, property_specs, path))

        return matches

    def match_resource_properties(self, properties, resource_type, path, cfn):
        """Check CloudFormation Properties"""
        matches = list()

        specs = RESOURCE_SPECS.get(cfn.regions[0]).get(
            'ResourceTypes').get(resource_type, {}).get('Properties', {})
        resource_specs = RESOURCE_SPECS.get(cfn.regions[0]).get('ResourceTypes').get(resource_type)
        matches.extend(self.check(cfn, properties, specs, resource_specs, path))

        return matches
