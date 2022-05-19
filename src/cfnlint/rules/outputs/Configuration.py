"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch
from cfnlint.helpers import FUNCTIONS_SINGLE


class Configuration(CloudFormationLintRule):
    """Check if Outputs are configured correctly"""
    id = 'E6001'
    shortdesc = 'Outputs have appropriate properties'
    description = 'Making sure the outputs are properly configured'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/outputs-section-structure.html'
    tags = ['outputs']

    valid_keys = [
        'Value',
        'Export',
        'Description',
        'Condition'
    ]

    # Map can be singular or multiple for this case we are going to skip
    valid_funcs = FUNCTIONS_SINGLE + ['Fn::FindInMap', 'Fn::Transform']

    def check_func(self, value, path):
        """ Check that a value is using the correct functions """
        matches = []
        if isinstance(value, dict):
            if len(value) == 1:
                for k in value.keys():
                    if k not in self.valid_funcs:
                        message = '{0} must use one of the functions {1}'
                        matches.append(RuleMatch(
                            path,
                            message.format('/'.join(path), self.valid_funcs)
                        ))
            else:
                message = '{0} must use one of the functions {1}'
                matches.append(RuleMatch(
                    path,
                    message.format('/'.join(path), self.valid_funcs)
                ))
        elif isinstance(value, (list)):
            message = '{0} must be a string or one of the functions {1}'
            matches.append(RuleMatch(
                path,
                message.format('/'.join(path), self.valid_funcs)
            ))

        return matches

    def check_export(self, value, path):
        """ Check export structure"""
        matches = []
        if isinstance(value, dict):
            if len(value) == 1:
                for k, v in value.items():
                    if k != 'Name':
                        message = '{0} must be a an object of one with key "Name"'
                        matches.append(RuleMatch(
                            path,
                            message.format('/'.join(path))
                        ))
                    else:
                        matches.extend(self.check_func(v, path[:] + ['Name']))
            else:
                message = '{0} must be a an object of one with key "Name"'
                matches.append(RuleMatch(
                    path,
                    message.format('/'.join(path))
                ))
        else:
            message = '{0} must be a an object of one with key "Name"'
            matches.append(RuleMatch(
                path,
                message.format('/'.join(path))
            ))

        return matches

    def match(self, cfn):
        matches = []

        outputs = cfn.template.get('Outputs', {})
        if outputs:
            if isinstance(outputs, dict):
                for output_name, output_value in outputs.items():
                    if not isinstance(output_value, dict):
                        message = 'Output {0} is not an object'
                        matches.append(RuleMatch(
                            ['Outputs', output_name],
                            message.format(output_name)
                        ))
                    else:
                        for propname, propvalue in output_value.items():
                            if propname not in self.valid_keys:
                                message = 'Output {0} has invalid property {1}'
                                matches.append(RuleMatch(
                                    ['Outputs', output_name, propname],
                                    message.format(output_name, propname)
                                ))
                            else:
                                if propvalue is None:
                                    message = 'Output {0} has property {1} has invalid type'
                                    matches.append(RuleMatch(
                                        ['Outputs', output_name, propname],
                                        message.format(output_name, propname)
                                    ))
                        value = output_value.get('Value')
                        if value:
                            matches.extend(self.check_func(value, ['Outputs', output_name, 'Value']))
                        export = output_value.get('Export')
                        if export:
                            matches.extend(self.check_export(
                                export, ['Outputs', output_name, 'Export']))
            else:
                matches.append(RuleMatch(['Outputs'], 'Outputs do not follow correct format.'))

        return matches
