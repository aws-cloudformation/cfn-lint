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


class Ref(CloudFormationLintRule):
    """Check if Ref value is a string"""
    id = 'E1020'
    shortdesc = 'Ref validation of value'
    description = 'Making the Ref has a value of String (no other functions are supported)'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-ref.html'
    tags = ['functions', 'ref']

    def match(self, cfn):
        """Check CloudFormation Ref"""

        matches = []

        ref_objs = cfn.search_deep_keys('Ref')

        for ref_obj in ref_objs:
            value = ref_obj[-1]
            if not isinstance(value, (six.string_types, six.text_type)):
                message = 'Ref can only be a string for {0}'
                matches.append(RuleMatch(ref_obj[:-1], message.format('/'.join(map(str, ref_obj[:-1])))))

        return matches
