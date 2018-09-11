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
from cfnlint.helpers import LIMITS


class LimitName(CloudFormationLintRule):
    """Check if maximum Mapping name size limit is exceeded"""
    id = 'E7011'
    shortdesc = 'Mapping name limit not exceeded'
    description = 'Check the size of Mapping names in the template is less than the upper limit'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cloudformation-limits.html'
    tags = ['mappings', 'limits']

    def match(self, cfn):
        """Check CloudFormation Mappings"""

        matches = []

        mappings = cfn.template.get('Mappings', {})

        for mapping_name in mappings:
            path = ['Mappings', mapping_name]
            if len(mapping_name) > LIMITS['mappings']['name']:
                message = 'The length of mapping name ({0}) exceeds the limit ({1})'
                matches.append(RuleMatch(path, message.format(len(mapping_name), LIMITS['mappings']['name'])))

        return matches
