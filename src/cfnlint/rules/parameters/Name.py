"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import re
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch
from cfnlint.helpers import REGEX_ALPHANUMERIC


class Name(CloudFormationLintRule):
    """Check if Parameters are named correctly"""
    id = 'E2003'
    shortdesc = 'Parameters have appropriate names'
    description = 'Check if Parameters are properly named (A-Za-z0-9)'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/parameters-section-structure.html#parameters-section-structure-requirements'
    tags = ['parameters']

    def match(self, cfn):
        """Check CloudFormation Mapping"""

        matches = []

        parameters = cfn.template.get('Parameters', {})
        for parameter_name, _ in parameters.items():
            if not re.match(REGEX_ALPHANUMERIC, parameter_name):
                message = 'Parameter {0} has invalid name.  Name has to be alphanumeric.'
                matches.append(RuleMatch(
                    ['Parameters', parameter_name],
                    message.format(parameter_name)
                ))

        return matches
