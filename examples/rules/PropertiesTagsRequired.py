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


class PropertiesTagsRequired(CloudFormationLintRule):
    """Check if Tags have required keys"""
    id = 'E9000'
    shortdesc = 'Tags have correct key values'
    description = 'Check Tags for resources'
    tags = ['resources', 'tags']

    def match(self, cfn):
        """Check Tags for required keys"""

        matches = []

        required_tags = ['CostCenter', 'ApplicationName']

        all_tags = cfn.search_deep_keys('Tags')
        all_tags = [x for x in all_tags if x[0] == 'Resources']
        for all_tag in all_tags:
            all_keys = [d.get('Key') for d in all_tag[-1]]
            for required_tag in required_tags:
                if required_tag not in all_keys:
                    message = "Missing Tag {0} at {1}"
                    matches.append(
                        RuleMatch(
                            all_tag[:-1],
                            message.format(required_tag, '/'.join(map(str, all_tag[:-1])))))

        return matches
