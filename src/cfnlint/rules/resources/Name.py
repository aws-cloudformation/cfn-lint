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
import re
from cfnlint import CloudFormationLintRule
from cfnlint import RuleMatch
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
