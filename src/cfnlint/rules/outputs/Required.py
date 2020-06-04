"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class Required(CloudFormationLintRule):
    """Check if Outputs have required properties"""
    id = 'E6002'
    shortdesc = 'Outputs have required properties'
    description = 'Making sure the outputs have required properties'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/outputs-section-structure.html'
    tags = ['outputs']

    def match(self, cfn):
        matches = []

        outputs = cfn.template.get('Outputs', {})
        if outputs:
            for output_name, output_value in outputs.items():
                if 'Value' not in output_value:
                    message = 'Output {0} is missing property {1}'
                    matches.append(RuleMatch(
                        ['Outputs', output_name, 'Value'],
                        message.format(output_name, 'Value')
                    ))

        return matches
