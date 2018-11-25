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
import regex
from cfnlint import CloudFormationLintRule
from cfnlint import RuleMatch


class ManagedPolicyDescription(CloudFormationLintRule):
    """Check if IAM Policy Description is syntax correct"""
    id = 'E3507'
    shortdesc = 'Check if IAM Managed Policy description follows supported regex'
    description = 'IAM Managed Policy description much comply with the regex [\\p{L}\\p{M}\\p{Z}\\p{S}\\p{N}\\p{P}]*'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-iam-managedpolicy.html'
    tags = ['properties', 'iam']

    def __init__(self):
        """Init"""
        super(ManagedPolicyDescription, self).__init__()
        self.resource_property_types.append('AWS::IAM::ManagedPolicy')

    def check_value(self, value, path):
        """Check the value"""
        regex_string = r'^[\p{L}\p{M}\p{Z}\p{S}\p{N}\p{P}]+$'
        r = regex.compile(regex_string)
        if not r.match(value):
            message = 'ManagedPolicy Description needs to follow regex pattern "{0}"'
            return [
                RuleMatch(path[:], message.format(regex_string))
            ]

        return []

    def match_resource_properties(self, properties, _, path, cfn):
        """Check CloudFormation Properties"""
        matches = []

        matches.extend(
            cfn.check_value(
                obj=properties, key='Description',
                path=path[:],
                check_value=self.check_value
            ))

        return matches
