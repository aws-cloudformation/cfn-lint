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


class LimitAttributes(CloudFormationLintRule):
    """Check if maximum Mapping attribute limit is exceeded"""
    id = 'E7012'
    shortdesc = 'Mapping attribute limit not exceeded'
    description = 'Check if the amount of Mapping attributes in the template is less than the upper limit'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cloudformation-limits.html'
    tags = ['mappings', 'limits']

    def match(self, cfn):
        """Check CloudFormation Mappings"""

        matches = []

        mappings = cfn.template.get('Mappings', {})

        for mapping_name, mapping in mappings.items():

            for mapping_attribute_name, mapping_attribute in mapping.items():
                path = ['Mappings', mapping_name, mapping_attribute_name]
                if len(mapping_attribute) > LIMITS['mappings']['attributes']:
                    message = 'The amount of mapping attributes ({0}) exceeds the limit ({1})'
                    matches.append(RuleMatch(path, message.format(len(mapping_attribute), LIMITS['mappings']['attributes'])))

        return matches
