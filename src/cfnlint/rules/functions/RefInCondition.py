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


class RefInCondition(CloudFormationLintRule):
    """Check if Ref value is a string"""
    id = 'E1026'
    shortdesc = 'Cannot reference resources in the Conditions block of the template'
    description = 'Check that any Refs in the Conditions block uses no resources'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-conditions.html#w2ab2c21c28c21c45'
    tags = ['functions', 'ref']

    def match(self, cfn):
        """Check CloudFormation Ref"""

        matches = []

        ref_objs = cfn.search_deep_keys('Ref')
        resource_names = cfn.get_resource_names()

        for ref_obj in ref_objs:
            if ref_obj[0] == 'Conditions':
                value = ref_obj[-1]
                if isinstance(value, (six.string_types, six.text_type, int)):
                    if value in resource_names:
                        message = 'Cannot reference resource {0} in the Conditions block of the template at {1}'
                        matches.append(RuleMatch(ref_obj[:-1], message.format(value, '/'.join(map(str, ref_obj[:-1])))))

        return matches
