"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import six
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class GetAz(CloudFormationLintRule):
    """Check if GetAz values are correct"""
    id = 'E1015'
    shortdesc = 'GetAz validation of parameters'
    description = 'Making sure the function not is of list'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-getavailabilityzones.html'
    tags = ['functions', 'getaz']

    def match(self, cfn):
        matches = []

        getaz_objs = cfn.search_deep_keys('Fn::GetAZs')

        for getaz_obj in getaz_objs:
            getaz_value = getaz_obj[-1]
            if isinstance(getaz_value, six.string_types):
                if getaz_value != '' and getaz_value not in cfn.regions:
                    message = 'GetAZs should be of empty or string of valid region for {0}'
                    matches.append(RuleMatch(
                        getaz_obj[:-1], message.format('/'.join(map(str, getaz_obj[:-1])))))
            elif isinstance(getaz_value, dict):
                if len(getaz_value) == 1:
                    if isinstance(getaz_value, dict):
                        for key, value in getaz_value.items():
                            if key != 'Ref' or value != 'AWS::Region':
                                message = 'GetAZs should be of Ref to AWS::Region for {0}'
                                matches.append(RuleMatch(
                                    getaz_obj[:-1], message.format('/'.join(map(str, getaz_obj[:-1])))))
                    else:
                        message = 'GetAZs should be of Ref to AWS::Region for {0}'
                        matches.append(RuleMatch(
                            getaz_obj[:-1], message.format('/'.join(map(str, getaz_obj[:-1])))))
                else:
                    message = 'GetAZs should be of Ref to AWS::Region for {0}'
                    matches.append(RuleMatch(
                        getaz_obj[:-1], message.format('/'.join(map(str, getaz_obj[:-1])))))
        return matches
