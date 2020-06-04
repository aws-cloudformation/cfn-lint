"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class Base(CloudFormationLintRule):
    """Check Base Template Settings"""
    id = 'E1001'
    shortdesc = 'Basic CloudFormation Template Configuration'
    description = 'Making sure the basic CloudFormation template components are properly configured'
    source_url = 'https://github.com/aws-cloudformation/cfn-python-lint'
    tags = ['base']

    required_keys = [
        'Resources'
    ]

    def match(self, cfn):
        matches = []

        top_level = []
        for x in cfn.template:
            top_level.append(x)
            if x not in cfn.sections:
                message = 'Top level template section {0} is not valid'
                matches.append(RuleMatch([x], message.format(x)))

        for y in self.required_keys:
            if y not in top_level:
                message = 'Missing top level template section {0}'
                matches.append(RuleMatch([y], message.format(y)))

        return matches
