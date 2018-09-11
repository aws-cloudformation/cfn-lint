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
from cfnlint.helpers import FUNCTIONS


class Aliases(CloudFormationLintRule):
    """Check if CloudFront Aliases are valid domain names"""
    id = 'E3013'
    shortdesc = 'CloudFront Aliases'
    description = 'CloudFront aliases should contain valid domain names'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-cloudfront-distribution-distributionconfig.html#cfn-cloudfront-distribution-distributionconfig-aliases'
    tags = ['properties', 'cloudfront']

    def match(self, cfn):
        """Check cloudfront Resource Parameters"""

        matches = []

        valid_domain = re.compile(r'^(?:[a-z0-9\*](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]$')

        results = cfn.get_resource_properties(['AWS::CloudFront::Distribution', 'DistributionConfig'])
        for result in results:
            aliases = result['Value'].get('Aliases')
            if aliases:
                for alias in aliases:
                    if isinstance(alias, str) and alias not in FUNCTIONS:
                        wildcard = alias.split('.')
                        if '*' in wildcard[1:]:
                            message = 'Invalid use of wildcards: {}'.format(alias)
                            path = result['Path'] + ['Aliases']
                            matches.append(RuleMatch(path, message.format(('/'.join(result['Path'])))))
                        if not re.match(valid_domain, alias):
                            message = 'Invalid alias found: {}'.format(alias)
                            path = result['Path'] + ['Aliases']
                            matches.append(RuleMatch(path, message.format(('/'.join(result['Path'])))))

        return matches
