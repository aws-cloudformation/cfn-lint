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
import six
from cfnlint import CloudFormationLintRule
from cfnlint import RuleMatch


class GetAz(CloudFormationLintRule):
    """Check if GetAz values are correct"""
    id = 'E1015'
    shortdesc = 'GetAz validation of parameters'
    description = 'Making sure the function not is of list'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-getavailabilityzones.html'
    tags = ['functions', 'getaz']

    def match(self, cfn):
        """Check CloudFormation GetAz"""

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
