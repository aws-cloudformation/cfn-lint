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
from __future__ import unicode_literals
import re
import six
from cfnlint import CloudFormationLintRule
from cfnlint import RuleMatch


class Used(CloudFormationLintRule):
    """Check if Parameters are used"""
    id = 'W2001'
    shortdesc = 'Check if Parameters are Used'
    description = 'Making sure the parameters defined are used'
    source_url = 'https://github.com/awslabs/cfn-python-lint'
    tags = ['parameters']

    def searchstring(self, string, parameter):
        """Search string for tokenized fields"""
        regex = re.compile(r'\${(%s)}' % parameter)
        return regex.findall(string)

    def isparaminref(self, subs, parameter):
        """Search sub strings for parameters"""
        for sub in subs:
            if isinstance(sub, (six.text_type, six.string_types)):
                if self.searchstring(sub, parameter):
                    return True

        return False

    def match(self, cfn):
        """Check CloudFormation Parameters"""

        matches = []

        reftrees = cfn.search_deep_keys('Ref')
        refs = []
        for reftree in reftrees:
            refs.append(reftree[-1])
        subtrees = cfn.search_deep_keys('Fn::Sub')
        subs = []
        for subtree in subtrees:
            if isinstance(subtree[-1], list):
                subs.extend(cfn.get_sub_parameters(subtree[-1][0]))
            else:
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
