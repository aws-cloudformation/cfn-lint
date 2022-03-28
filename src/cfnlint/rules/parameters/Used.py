"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from __future__ import unicode_literals
import re
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class Used(CloudFormationLintRule):
    """Check if Parameters are used"""
    id = 'W2001'
    shortdesc = 'Check if Parameters are Used'
    description = 'Making sure the parameters defined are used'
    source_url = 'https://github.com/aws-cloudformation/cfn-python-lint'
    tags = ['parameters']

    def searchstring(self, string, parameter):
        """Search string for tokenized fields"""
        regex = re.compile(r'\${(%s)}' % parameter)
        return regex.findall(string)

    def isparaminref(self, subs, parameter):
        """Search sub strings for parameters"""
        for sub in subs:
            if isinstance(sub, (str)):
                if self.searchstring(sub, parameter):
                    return True

        return False

    def match(self, cfn):
        matches = []

        reftrees = cfn.transform_pre.get('Ref')
        subtrees = cfn.transform_pre.get('Fn::Sub')
        refs = []
        for reftree in reftrees:
            refs.append(reftree[-1])
        subs = []
        for subtree in subtrees:
            if isinstance(subtree[-1], list):
                subs.extend(cfn.get_sub_parameters(subtree[-1][0]))
            elif isinstance(subtree[-1], str):
                subs.extend(cfn.get_sub_parameters(subtree[-1]))

        for paramname, _ in cfn.get_parameters().items():
            if paramname not in refs:
                if paramname not in subs:
                    message = 'Parameter {0} not used.'
                    matches.append(RuleMatch(
                        ['Parameters', paramname],
                        message.format(paramname)
                    ))

        return matches
