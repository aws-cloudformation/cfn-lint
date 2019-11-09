"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import re
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch
from cfnlint.helpers import REGEX_ALPHANUMERIC


class Name(CloudFormationLintRule):
    """Check if Mappings are named correctly"""
    id = 'E7002'
    shortdesc = 'Mappings have appropriate names'
    description = 'Check if Mappings are properly named (A-Za-z0-9)'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/mappings-section-structure.html'
    tags = ['mapping']

    def match(self, cfn):
        """Check CloudFormation Mapping"""

        matches = []

        mappings = cfn.template.get('Mappings', {})
        for mapping_name, _ in mappings.items():
            if not re.match(REGEX_ALPHANUMERIC, mapping_name):
                message = 'Mapping {0} has invalid name.  Name has to be alphanumeric.'
                matches.append(RuleMatch(
                    ['Mappings', mapping_name],
                    message.format(mapping_name)
                ))

        return matches
