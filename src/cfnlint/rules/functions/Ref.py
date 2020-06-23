"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import six
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class Ref(CloudFormationLintRule):
    """Check if Ref value is a string"""
    id = 'E1020'
    shortdesc = 'Ref validation of value'
    description = 'Making the Ref has a value of String (no other functions are supported)'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-ref.html'
    tags = ['functions', 'ref']

    def match(self, cfn):
        matches = []

        ref_objs = cfn.search_deep_keys('Ref')
        for ref_obj in ref_objs:
            value = ref_obj[-1]
            if not isinstance(value, (six.string_types)):
                message = 'Ref can only be a string for {0}'
                matches.append(
                    RuleMatch(ref_obj[:-1], message.format('/'.join(map(str, ref_obj[:-1])))))

        return matches
