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
from cfnlint.helpers import LIMITS


class LimitValue(CloudFormationLintRule):
    """Check if maximum Parameter value size limit is exceeded"""
    id = 'E2012'
    shortdesc = 'Parameter value limit not exceeded'
    description = 'Check if the size of Parameter values in the template is less than the upper limit'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cloudformation-limits.html'
    tags = ['parameters', 'limits']

    def match(self, cfn):
        """Check CloudFormation Parameters"""

        matches = []

        value_limit = LIMITS['parameters']['value']

        # There are no real "Values" in the template, check the "meta" information
        # (Default, ALlowedValue and MaxLength) against the limnit
        for paramname, paramvalue in cfn.get_parameters().items():

            # Check Default value
            default_value = paramvalue.get('Default')

            if isinstance(default_value, (six.text_type, six.string_types)):
                if len(default_value) > value_limit:
                    path = ['Parameters', paramname, 'Default']
                    message = 'The length of parameter default value ({0}) exceeds the limit ({1})'
                    matches.append(RuleMatch(path, message.format(len(default_value), value_limit)))

            # CHeck MaxLength parameters
            max_length = paramvalue.get('MaxLength', 0)

            if isinstance(max_length, (six.text_type, six.string_types)):
                try:
                    max_length = int(max_length)
                except ValueError:
                    # Configuration errors are not the responsibility of this rule
                    max_length = 0

            if isinstance(max_length, six.integer_types):
                if max_length > value_limit:
                    path = ['Parameters', paramname, 'MaxLength']
                    message = 'The MaxLength of parameter ({0}) exceeds the limit ({1})'
                    matches.append(RuleMatch(path, message.format(max_length, value_limit)))

            # Check AllowedValues
            allowed_values = paramvalue.get('AllowedValues', [])

            for allowed_value in allowed_values:
                if isinstance(allowed_value, (six.text_type, six.string_types)):
                    if len(allowed_value) > value_limit:
                        path = ['Parameters', paramname, 'AllowedValues']
                        message = 'The length of parameter allowed value ({0}) exceeds the limit ({1})'
                        matches.append(RuleMatch(path, message.format(len(allowed_value), value_limit)))

        return matches
