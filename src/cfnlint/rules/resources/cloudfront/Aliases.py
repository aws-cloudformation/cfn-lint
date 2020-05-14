"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import re
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch
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

        valid_domain = re.compile(
            r'^(?:[a-z0-9\*](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]$')

        results = cfn.get_resource_properties(
            ['AWS::CloudFront::Distribution', 'DistributionConfig'])
        for result in results:
            aliases = result['Value'].get('Aliases')
            if aliases:
                for alias in aliases:
                    if isinstance(alias, str) and alias not in FUNCTIONS:
                        wildcard = alias.split('.')
                        if '*' in wildcard[1:]:
                            message = 'Invalid use of wildcards: {}'.format(alias)
                            path = result['Path'] + ['Aliases']
                            matches.append(
                                RuleMatch(path, message.format(('/'.join(result['Path'])))))
                        if not re.match(valid_domain, alias):
                            message = 'Invalid alias found: {}'.format(alias)
                            path = result['Path'] + ['Aliases']
                            matches.append(
                                RuleMatch(path, message.format(('/'.join(result['Path'])))))

        return matches
