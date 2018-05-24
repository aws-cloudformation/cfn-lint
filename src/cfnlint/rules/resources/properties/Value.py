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


class Value(CloudFormationLintRule):
    """Check if Resource Properties are correct"""
    id = 'E3011'
    shortdesc = 'Check values for appropriate values'
    description = 'Checks resource properties for Ref and GetAtt values'
    tags = ['base', 'resources']

    def __init__(self, ):
        """Init """
        valuespec = cfnlint.helpers.load_resources('data/AdditionalSpecs/PropertyValues.json')
        self.resource_value_specs = valuespec.get('ResourceTypes', {})
        self.property_value_specs = valuespec.get('PropertyTypes', {})
        self.parameter_type_specs = valuespec.get('ParameterTypes', {})
        self.value_type_specs = valuespec.get('ValueTypes', {})
        for resource_type_spec in self.resource_value_specs:
            self.resource_property_types.append(resource_type_spec)
        for property_type_spec in self.property_value_specs:
            self.resource_sub_property_types.append(property_type_spec)

    def check_value_ref(self, value, path, **kwargs):
        """Check Ref"""
        matches = list()
        cfn = kwargs.get('cfn')
        value_specs = kwargs.get('value_specs', {}).get('Ref')
        list_value_specs = kwargs.get('list_value_specs', {}).get('Ref')
        property_type = kwargs.get('property_type')
        property_name = kwargs.get('property_name')

        if path[-1] == 'Ref' and property_type == 'List' and path[-2] == property_name:
            specs = list_value_specs
        else:
            specs = value_specs

        if not specs:
            message = 'Property {0} has no valid Refs at {1}'
            matches.append(RuleMatch(path, message.format(path[-2], '/'.join(map(str, path)))))
            return matches
        if value in cfn.template.get('Parameters', {}):
            param = cfn.template.get('Parameters').get(value)
            parameter_type = param.get('Type')
            valid_parameter_types = []
            for parameter in specs.get('Parameters'):
                for parameter_type in self.parameter_type_specs.get(parameter):
                    valid_parameter_types.append(parameter_type)

            if not specs.get('Parameters'):
                message = 'Property {0} has no valid Refs to Parameters at {1}'
                matches.append(RuleMatch(path, message.format(path[-2], '/'.join(map(str, path)))))
            elif parameter_type not in valid_parameter_types:
                message = 'Property {0} can Ref to parameter of types [{1}] at {2}'
                matches.append(
                    RuleMatch(
                        path,
                        message.format(
                            path[-2],
                            ', '.join(map(str, valid_parameter_types)),
                            '/'.join(map(str, path)))))
        elif value in cfn.template.get('Resources', {}):
            resource = cfn.template.get('Resources').get(value)
            resource_type = resource.get('Type')
            if not specs.get('Resources'):
                message = 'Property {0} has no valid Refs to Resources at {1}'
                matches.append(RuleMatch(path, message.format(path[-2], '/'.join(map(str, path)))))
            elif resource_type not in specs.get('Resources'):
                message = 'Property {0} can Ref to resources of types [{1}] at {2}'
                matches.append(
                    RuleMatch(
                        path,
                        message.format(
                            path[-2],
                            ', '.join(map(str, specs.get('Resources'))),
                            '/'.join(map(str, path)))))

        return matches

    def check_value_getatt(self, value, path, **kwargs):
        """Check GetAtt"""
        matches = list()
        cfn = kwargs.get('cfn')
        specs = kwargs.get('value_specs', {}).get('GetAtt')
        if not specs:
            message = 'Property {0} has no valid Fn::GetAtt options at {1}'
            matches.append(RuleMatch(path, message.format(value[-2], '/'.join(map(str, path)))))
            return matches
        resource_type = cfn.template.get('Resources', {}).get(value[0], {}).get('Type')
        if resource_type not in specs:
            message = 'Property {0} can Fn::GetAtt to a resource of types [{1}] at {2}'
            matches.append(
                RuleMatch(
                    path,
                    message.format(
                        path[-2],
                        ', '.join(map(str, specs)),
                        '/'.join(map(str, path)))))
        elif value[1] != specs[resource_type]:
            message = 'Property {0} can Fn::GetAtt to a resource attribute "{1}" at {2}'
            matches.append(
                RuleMatch(
                    path,
                    message.format(
                        path[-2],
                        specs[resource_type],
                        '/'.join(map(str, path)))))

        return matches

    def check(self, cfn, properties, value_specs, property_specs, path):
        """Check itself"""
        matches = list()

        for prop in properties:
            if prop in value_specs:
                value_type = value_specs.get(prop).get('Value', {}).get('ValueType', '')
                list_value_type = value_specs.get(prop).get('Value', {}).get('ListValueType', '')
                property_type = property_specs.get('Properties').get(prop).get('Type')
                matches.extend(
                    cfn.check_value(
                        properties, prop, path,
                        check_ref=self.check_value_ref,
                        check_getatt=self.check_value_getatt,
                        value_specs=self.value_type_specs.get(value_type, {}),
                        list_value_specs=self.value_type_specs.get(list_value_type, {}),
                        cfn=cfn, property_type=property_type, property_name=prop
                    )
                )

        return matches

    def match_resource_sub_properties(self, properties, property_type, path, cfn):
        """Match for sub properties"""
        matches = list()

        specs = self.property_value_specs.get(property_type, {}).get('Properties', {})
        property_specs = cfnlint.helpers.RESOURCE_SPECS.get('us-east-1').get('PropertyTypes').get(property_type)
        matches.extend(self.check(cfn, properties, specs, property_specs, path))

        return matches

    def match_resource_properties(self, properties, resource_type, path, cfn):
        """Check CloudFormation Properties"""
        matches = list()
        specs = self.resource_value_specs.get(resource_type, {}).get('Properties', {})
        resource_specs = cfnlint.helpers.RESOURCE_SPECS.get('us-east-1').get('ResourceTypes').get(resource_type)
        matches.extend(self.check(cfn, properties, specs, resource_specs, path))

        return matches
