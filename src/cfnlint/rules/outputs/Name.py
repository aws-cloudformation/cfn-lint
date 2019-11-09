"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import re
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch
from cfnlint.helpers import REGEX_ALPHANUMERIC


class Name(CloudFormationLintRule):
    """Check if Outputs are named correctly"""
    id = 'E6004'
    shortdesc = 'Outputs have appropriate names'
    description = 'Check if Outputs are properly named (A-Za-z0-9)'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/outputs-section-structure.html'
    tags = ['outputs']

    def match(self, cfn):
        """Check CloudFormation Mapping"""

        matches = []

        outputs = cfn.template.get('Outputs', {})
        for output_name, _ in outputs.items():
            if not re.match(REGEX_ALPHANUMERIC, output_name):
                message = 'Output {0} has invalid name.  Name has to be alphanumeric.'
                matches.append(RuleMatch(
                    ['Outputs', output_name],
                    message.format(output_name)
                ))

        return matches
