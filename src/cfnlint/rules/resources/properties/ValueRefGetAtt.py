"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import six
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch
from cfnlint.helpers import RESOURCE_SPECS
import cfnlint.helpers


class ValueRefGetAtt(CloudFormationLintRule):
    """Check if Resource Properties are correct"""
    id = 'E3008'
    shortdesc = 'Check values of properties for valid Refs and GetAtts'
    description = 'Checks resource properties for Ref and GetAtt values'
    tags = ['resources', 'ref', 'getatt']

    def initialize(self, cfn):
        """Initialize the rule"""
        for resource_type_spec in RESOURCE_SPECS.get(cfn.regions[0]).get('ResourceTypes'):
            self.resource_property_types.append(resource_type_spec)
        for property_type_spec in RESOURCE_SPECS.get(cfn.regions[0]).get('PropertyTypes'):
            self.resource_sub_property_types.append(property_type_spec)

    def is_value_a_list(self, path, property_name):
        """
            Determines if the value checked is a list or a value in a list
            We need to handle conditions in the path that could be nested, etc.
            ['Resources', 'LoadBalancer', 'Properties', 'Subnets', 'Fn::If', 2, 'Fn::If', 2]
            Numbers preceeded by a Fn::If should be removed and check repeated.
        """
        if path[-1] != property_name:
            # Property doesn't match the property name
            # Check if its a number and a condition
            if isinstance(path[-1], int) and path[-2] == 'Fn::If':
                return self.is_value_a_list(path[:-2], property_name)

            return False

        return True

    def check_value_ref(self, value, path, **kwargs):
        """Check Ref"""
        matches = list()
        cfn = kwargs.get('cfn')
        value_specs = kwargs.get('value_specs', {}).get('Ref')
        list_value_specs = kwargs.get('list_value_specs', {}).get('Ref')
        property_type = kwargs.get('property_type')
        property_name = kwargs.get('property_name')
        if path[-1] == 'Ref' and property_type == 'List' and self.is_value_a_list(path[:-1], property_name):
            specs = list_value_specs
        else:
            specs = value_specs

        if not specs:
            # If no Ref's are specified, just skip
            # Opposite of GetAtt you will always have a Ref to a Parameter so if this is
            # None it just hasn't been defined and we can skip
            return matches

        if value in cfn.template.get('Parameters', {}):
            param = cfn.template.get('Parameters').get(value, {})
            parameter_type = param.get('Type')
            valid_parameter_types = []
            for parameter in specs.get('Parameters'):
                for param_type in RESOURCE_SPECS.get(cfn.regions[0]).get('ParameterTypes').get(parameter):
                    valid_parameter_types.append(param_type)

            if not specs.get('Parameters'):
                message = 'Property "{0}" has no valid Refs to Parameters at {1}'
                matches.append(RuleMatch(path, message.format(
                    property_name, '/'.join(map(str, path)))))
            elif parameter_type not in valid_parameter_types:
                message = 'Property "{0}" can Ref to parameter of types [{1}] at {2}'
                matches.append(
                    RuleMatch(
                        path,
                        message.format(
                            property_name,
                            ', '.join(map(str, valid_parameter_types)),
                            '/'.join(map(str, path)))))
        if value in cfn.template.get('Resources', {}):
            resource = cfn.template.get('Resources').get(value, {})
            resource_type = resource.get('Type')
            if not specs.get('Resources'):
                message = 'Property "{0}" has no valid Refs to Resources at {1}'
                matches.append(RuleMatch(path, message.format(
                    property_name, '/'.join(map(str, path)))))
            elif resource_type not in specs.get('Resources'):
                message = 'Property "{0}" can Ref to resources of types [{1}] at {2}'
                matches.append(
                    RuleMatch(
                        path,
                        message.format(
                            property_name,
                            ', '.join(map(str, specs.get('Resources'))),
                            '/'.join(map(str, path)))))

        return matches

    def check_value_getatt(self, value, path, **kwargs):
        """Check GetAtt"""
        matches = []
        cfn = kwargs.get('cfn')
        value_specs = kwargs.get('value_specs', {}).get('GetAtt')
        list_value_specs = kwargs.get('list_value_specs', {}).get('GetAtt')
        property_type = kwargs.get('property_type')
        property_name = kwargs.get('property_name')
        # You can sometimes get a list or a string with . in it
        if isinstance(value, list):
            resource_name = value[0]
            if len(value[1:]) == 1:
                resource_attribute = value[1].split('.')
            else:
                resource_attribute = value[1:]
        elif isinstance(value, six.string_types):
            resource_name = value.split('.')[0]
            resource_attribute = value.split('.')[1:]
        is_value_a_list = self.is_value_a_list(path[:-1], property_name)
        if path[-1] == 'Fn::GetAtt' and property_type == 'List' and is_value_a_list:
            specs = list_value_specs
        else:
            specs = value_specs

        resource_type = cfn.template.get('Resources', {}).get(resource_name, {}).get('Type')

        if cfnlint.helpers.is_custom_resource(resource_type):
            #  A custom resource voids the spec.  Move on
            return matches

        if resource_type == 'AWS::CloudFormation::Stack' and resource_attribute[0] == 'Outputs':
            # Nested Stack Outputs
            # if its a string type we are good and return matches
            # if its a list its a failure as Outputs can only be strings
            if is_value_a_list and property_type == 'List':
                message = 'CloudFormation stack outputs need to be strings not lists at {0}'
                matches.append(RuleMatch(path, message.format('/'.join(map(str, path)))))

            return matches

        if specs is None:
            # GetAtt specs aren't specified skip
            return matches
        if not specs:
            # GetAtt is specified but empty so there are no valid options
            message = 'Property "{0}" has no valid Fn::GetAtt options at {1}'
            matches.append(RuleMatch(path, message.format(property_name, '/'.join(map(str, path)))))
            return matches

        if resource_type not in specs:
            message = 'Property "{0}" can Fn::GetAtt to a resource of types [{1}] at {2}'
            matches.append(
                RuleMatch(
                    path,
                    message.format(
                        property_name,
                        ', '.join(map(str, specs)),
                        '/'.join(map(str, path)))))
        elif '.'.join(map(str, resource_attribute)) != specs[resource_type]:
            message = 'Property "{0}" can Fn::GetAtt to a resource attribute "{1}" at {2}'
            matches.append(
                RuleMatch(
                    path,
                    message.format(
                        property_name,
                        specs[resource_type],
                        '/'.join(map(str, path)))))

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
                        list_value_type = value.get('ListValueType', '')
                        property_type = property_specs.get('Properties').get(prop).get('Type')
                        matches.extend(
                            cfn.check_value(
                                p_value, prop, p_path,
                                check_ref=self.check_value_ref,
                                check_get_att=self.check_value_getatt,
                                value_specs=RESOURCE_SPECS.get(cfn.regions[0]).get(
                                    'ValueTypes').get(value_type, {}),
                                list_value_specs=RESOURCE_SPECS.get(cfn.regions[0]).get(
                                    'ValueTypes').get(list_value_type, {}),
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
