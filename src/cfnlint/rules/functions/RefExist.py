"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import re
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class RefExist(CloudFormationLintRule):
    id = 'E1012'
    shortdesc = 'Check if Refs exist'
    description = 'Making sure the refs exist'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-ref.html'
    tags = ['functions', 'ref']

    def searchstring(self, string):
        """Search string for tokenized fields"""
        regex = re.compile(r'\${([a-zA-Z0-9]*)}')
        return regex.findall(string)

    def match(self, cfn):
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
            if isinstance(ref, (str, int)):
                if ref not in valid_refs:
                    message = 'Ref {0} not found as a resource or parameter'
                    matches.append(RuleMatch(
                        reftree[:-2], message.format(ref)
                    ))

        return matches
