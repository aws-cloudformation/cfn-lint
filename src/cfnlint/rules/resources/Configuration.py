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


class Configuration(CloudFormationLintRule):
    """Check Base Resource Configuration"""
    id = 'E3001'
    shortdesc = 'Basic CloudFormation Resource Check'
    description = 'Making sure the basic CloudFormation resources ' + \
                  'are properly configured'
    source_url = 'https://github.com/awslabs/cfn-python-lint'
    tags = ['resources']

    def match(self, cfn):
        """Check CloudFormation Resources"""

        matches = []

        valid_attributes = [
            'CreationPolicy',
            'DeletionPolicy',
            'DependsOn',
            'Metadata',
            'UpdatePolicy',
            'Properties',
            'Type',
            'Condition'
        ]

        valid_custom_attributes = [
            'Version',
            'Properties',
            'DependsOn',
            'Metadata',
            'Condition',
            'Type',
        ]

        resources = cfn.template.get('Resources', {})
        if not isinstance(resources, dict):
            message = 'Resource not properly configured'
            matches.append(RuleMatch(['Resources'], message))
        else:
            for resource_name, resource_values in cfn.template.get('Resources', {}).items():
                self.logger.debug('Validating resource %s base configuration', resource_name)
                if not isinstance(resource_values, dict):
                    message = 'Resource not properly configured at {0}'
                    matches.append(RuleMatch(
                        ['Resources', resource_name],
                        message.format(resource_name)
                    ))
                    continue
                resource_type = resource_values.get('Type', '')
                check_attributes = []
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

                resource_type = resource_values.get('Type', '')
                if not resource_type:
                    message = 'Type not defined for resource {0}'
                    matches.append(RuleMatch(
                        ['Resources', resource_name],
                        message.format(resource_name)
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
                    resource_spec = cfnlint.helpers.RESOURCE_SPECS['us-east-1']
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
