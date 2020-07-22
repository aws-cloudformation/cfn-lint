"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import six
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch
import cfnlint.helpers


class Configuration(CloudFormationLintRule):
    """Check Base Resource Configuration"""
    id = 'E3001'
    shortdesc = 'Basic CloudFormation Resource Check'
    description = 'Making sure the basic CloudFormation resources are properly configured'
    source_url = 'https://github.com/aws-cloudformation/cfn-python-lint'
    tags = ['resources']


    def _check_resource(self, cfn, resource_name, resource_values):
        """ Check Resource """

        valid_attributes = [
            'Condition',
            'CreationPolicy',
            'DeletionPolicy',
            'DependsOn',
            'Metadata',
            'Properties',
            'Type',
            'UpdatePolicy',
            'UpdateReplacePolicy',
        ]

        valid_custom_attributes = [
            'Condition',
            'DeletionPolicy',
            'DependsOn',
            'Metadata',
            'Properties',
            'Type',
            'UpdateReplacePolicy',
            'Version',
        ]

        matches = []
        if not isinstance(resource_values, dict):
            message = 'Resource not properly configured at {0}'
            matches.append(RuleMatch(
                ['Resources', resource_name],
                message.format(resource_name)
            ))
            return matches

        # validate condition is a string
        condition = resource_values.get('Condition', '')
        if not isinstance(condition, six.string_types):
            message = 'Condition for resource {0} should be a string'
            matches.append(RuleMatch(
                ['Resources', resource_name, 'Condition'],
                message.format(resource_name)
            ))

        resource_type = resource_values.get('Type', '')
        check_attributes = []
        if not isinstance(resource_type, six.string_types):
            message = 'Type has to be a string at {0}'
            matches.append(RuleMatch(
                ['Resources', resource_name],
                message.format('/'.join(['Resources', resource_name]))
            ))
            return matches

        # Type is valid continue analysis
        if resource_type.startswith('Custom::') or resource_type == 'AWS::CloudFormation::CustomResource':
            check_attributes = valid_custom_attributes
        else:
            check_attributes = valid_attributes

        for property_key, _ in resource_values.items():
            if property_key not in check_attributes:
                message = 'Invalid resource attribute {0} for resource {1}'
                matches.append(RuleMatch(
                    ['Resources', resource_name, property_key],
                    message.format(property_key, resource_name)))

        if not resource_type:
            message = 'Type not defined for resource {0}'
            matches.append(RuleMatch(
                ['Resources', resource_name],
                message.format(resource_name)
            ))
        elif not isinstance(resource_type, six.string_types):
            message = 'Type has to be a string at {0}'
            matches.append(RuleMatch(
                ['Resources', resource_name],
                message.format('/'.join(['Resources', resource_name]))
            ))
        else:
            self.logger.debug('Check resource types by region...')
            for region, specs in cfnlint.helpers.RESOURCE_SPECS.items():
                if region in cfn.regions:
                    if resource_type not in specs['ResourceTypes']:
                        if not resource_type.startswith(('Custom::', 'AWS::Serverless::')):
                            message = 'Invalid or unsupported Type {0} for resource {1} in {2}'
                            matches.append(RuleMatch(
                                ['Resources', resource_name, 'Type'],
                                message.format(resource_type, resource_name, region)
                            ))

        if 'Properties' not in resource_values:
            resource_spec = cfnlint.helpers.RESOURCE_SPECS[cfn.regions[0]]
            if resource_type in resource_spec['ResourceTypes']:
                properties_spec = resource_spec['ResourceTypes'][resource_type]['Properties']
                # pylint: disable=len-as-condition
                if len(properties_spec) > 0:
                    required = 0
                    for _, property_spec in properties_spec.items():
                        if property_spec.get('Required', False):
                            required += 1
                    if required > 0:
                        if resource_type == 'AWS::CloudFormation::WaitCondition' and 'CreationPolicy' in resource_values.keys():
                            self.logger.debug('Exception to required properties section as CreationPolicy is defined.')
                        else:
                            message = 'Properties not defined for resource {0}'
                            matches.append(RuleMatch(
                                ['Resources', resource_name],
                                message.format(resource_name)
                            ))

        return matches


    def match(self, cfn):
        matches = []

        resources = cfn.template.get('Resources', {})
        if not isinstance(resources, dict):
            message = 'Resource not properly configured'
            matches.append(RuleMatch(['Resources'], message))
        else:
            for resource_name, resource_values in cfn.template.get('Resources', {}).items():
                self.logger.debug('Validating resource %s base configuration', resource_name)
                matches.extend(self._check_resource(cfn, resource_name, resource_values))

        return matches
