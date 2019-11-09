"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


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

    def match(self, cfn):
        """Check CloudFormation Outputs"""

        matches = []

        outputs = cfn.template.get('Outputs', {})
        if outputs:
            if isinstance(outputs, dict):
                for output_name, output_value in outputs.items():
                    for prop in output_value:
                        if prop not in self.valid_keys:
                            message = 'Output {0} has invalid property {1}'
                            matches.append(RuleMatch(
                                ['Outputs', output_name, prop],
                                message.format(output_name, prop)
                            ))
            else:
                matches.append(RuleMatch(['Outputs'], 'Outputs do not follow correct format.'))

        return matches
