"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class Description(CloudFormationLintRule):
    """Check if Outputs Descriptions are only string values"""
    id = 'E6005'
    shortdesc = 'Outputs descriptions can only be strings'
    description = 'Outputs descriptions can only be strings'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/outputs-section-structure.html'
    tags = ['outputs']

    def match(self, cfn):
        matches = []

        outputs = cfn.get_outputs_valid()
        if outputs:
            for output_name, output_value in outputs.items():
                description = output_value.get('Description')
                if description:
                    if not isinstance(description, str):
                        message = 'Output Description can only be a string'
                        matches.append(RuleMatch(['Outputs', output_name, 'Description'], message))

        return matches
