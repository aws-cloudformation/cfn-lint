"""
  Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.

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
import six
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class RefExist(CloudFormationLintRule):
    """Check if Parameters are used"""
    id = 'E1012'
    shortdesc = 'Check if Refs exist'
    description = 'Making sure the refs exist'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-ref.html'
    tags = ['functions', 'ref']

    pseudoparams = [
        'AWS::AccountId',
        'AWS::NoValue',
        'AWS::NotificationARNs',
        'AWS::Partition',
        'AWS::Region',
        'AWS::StackId',
        'AWS::StackName',
        'AWS::URLSuffix',
    ]

    def searchstring(self, string):
        """Search string for tokenized fields"""
        regex = re.compile(r'\${([a-zA-Z0-9]*)}')
        return regex.findall(string)

    def match(self, cfn):
        """Check CloudFormation Parameters"""

        matches = []

        # Build the list of refs
        reftrees = cfn.search_deep_keys('Ref')
        refs = []
        for reftree in reftrees:
            refs.append(reftree[-1])

        valid_refs = cfn.get_valid_refs()

        # start with the basic ref calls
        for reftree in reftrees:
            ref = reftree[-1]
            if isinstance(ref, (six.string_types, six.text_type, int)):
                if ref not in valid_refs:
                    message = 'Ref {0} not found as a resource or parameter'
                    matches.append(RuleMatch(
                        reftree[:-2], message.format(ref)
                    ))

        return matches
