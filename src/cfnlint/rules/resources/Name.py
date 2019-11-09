"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import re
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch
from cfnlint.helpers import REGEX_ALPHANUMERIC


class Name(CloudFormationLintRule):
    """Check if Resources are named correctly"""
    id = 'E3006'
    shortdesc = 'Resources have appropriate names'
    description = 'Check if Resources are properly named (A-Za-z0-9)'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/resources-section-structure.html#resources-section-structure-logicalid'
    tags = ['resources']

    def match(self, cfn):
        """Check CloudFormation Mapping"""

        matches = []

        resources = cfn.template.get('Resources', {})
        for resource_name, _ in resources.items():
            if not re.match(REGEX_ALPHANUMERIC, resource_name):
                message = 'Resources {0} has invalid name.  Name has to be alphanumeric.'
                matches.append(RuleMatch(
                    ['Resources', resource_name],
                    message.format(resource_name)
                ))

        return matches
