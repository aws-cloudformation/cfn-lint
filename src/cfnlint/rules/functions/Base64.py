"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import six
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class Base64(CloudFormationLintRule):
    """Check if Base64 values are correct"""
    id = 'E1021'
    shortdesc = 'Base64 validation of parameters'
    description = 'Making sure the function not is of list'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-base64.html'
    tags = ['functions', 'base64']

    def match(self, cfn):
        matches = []

        base64_objs = cfn.search_deep_keys('Fn::Base64')
        for base64_obj in base64_objs:
            tree = base64_obj[:-1]
            value_obj = base64_obj[-1]
            if isinstance(value_obj, dict):
                if len(value_obj) == 1:
                    for key, _ in value_obj.items():
                        if key == 'Fn::Split':
                            message = 'Base64 needs a string at {0}'
                            matches.append(RuleMatch(
                                tree[:], message.format('/'.join(map(str, tree)))))
                else:
                    message = 'Base64 needs a string not a map or list at {0}'
                    matches.append(RuleMatch(
                        tree[:], message.format('/'.join(map(str, tree)))))
            elif not isinstance(value_obj, six.string_types):
                message = 'Base64 needs a string at {0}'
                matches.append(RuleMatch(
                    tree[:], message.format('/'.join(map(str, tree)))))

        return matches
