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


class SubParametersUsed(CloudFormationLintRule):
    """Check if Sub Parameters are used"""
    id = 'W1019'
    shortdesc = 'Sub validation of parameters'
    description = 'Validate that Fn::Sub Parameters are used'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-sub.html'
    tags = ['functions', 'sub']

    def _test_parameters(self, cfn, sub_string, parameters, tree):
        """Test if sub parmaeters are in the string"""

        matches = []
        sub_string_parameters = cfn.get_sub_parameters(sub_string)

        for parameter_name, _ in parameters.items():
            if parameter_name not in sub_string_parameters:
                message = 'Parameter {0} not used in Fn::Sub at {1}'
                matches.append(RuleMatch(
                    tree, message.format(parameter_name, '/'.join(map(str, tree[:] + [parameter_name])))))

        return matches

    def match(self, cfn):
        """Check CloudFormation Join"""

        matches = []

        sub_objs = cfn.search_deep_keys('Fn::Sub')

        for sub_obj in sub_objs:
            sub_value_obj = sub_obj[-1]
            tree = sub_obj[:-1]
            if isinstance(sub_value_obj, list):
                if len(sub_value_obj) == 2:
                    sub_string = sub_value_obj[0]
                    parameters = sub_value_obj[1]
                    if not isinstance(sub_string, six.string_types):
                        continue
                    if not isinstance(parameters, dict):
                        continue
                    else:
                        matches.extend(self._test_parameters(cfn, sub_string, parameters, tree + [1]))

        return matches
