"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import six
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch
from cfnlint.helpers import LIMITS


class LimitValue(CloudFormationLintRule):
    """Check maximum Parameter value size limit"""
    id = 'I2012'
    shortdesc = 'Parameter value limit'
    description = 'Check if the size of Parameter values in the template is approaching the upper limit'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/cloudformation-limits.html'
    tags = ['parameters', 'limits']

    def match(self, cfn):
        matches = []

        value_limit = LIMITS['Parameters']['value']

        # There are no real "Values" in the template, check the "meta" information
        # (Default, AllowedValue and MaxLength) against the limit
        for paramname, paramvalue in cfn.get_parameters().items():

            # Check Default value
            default_value = paramvalue.get('Default')

            if isinstance(default_value, (six.text_type, six.string_types)):
                if LIMITS['threshold'] * value_limit < len(default_value) <= value_limit:
                    path = ['Parameters', paramname, 'Default']
                    message = 'The length of parameter default value ({0}) is approaching the limit ({1})'
                    matches.append(RuleMatch(path, message.format(len(default_value), value_limit)))

            # Check MaxLength parameters
            max_length = paramvalue.get('MaxLength', 0)

            if isinstance(max_length, (six.text_type, six.string_types)):
                try:
                    max_length = int(max_length)
                except ValueError:
                    # Configuration errors are not the responsibility of this rule
                    max_length = 0

            if isinstance(max_length, six.integer_types):
                if LIMITS['threshold'] * value_limit < max_length <= value_limit:
                    path = ['Parameters', paramname, 'MaxLength']
                    message = 'The MaxLength of parameter ({0}) is approaching the limit ({1})'
                    matches.append(RuleMatch(path, message.format(max_length, value_limit)))

            # Check AllowedValues
            allowed_values = paramvalue.get('AllowedValues', [])

            for allowed_value in allowed_values:
                if isinstance(allowed_value, (six.text_type, six.string_types)):
                    if LIMITS['threshold'] * value_limit < len(allowed_value) <= value_limit:
                        path = ['Parameters', paramname, 'AllowedValues']
                        message = 'The length of parameter allowed value ({0}) is approaching the limit ({1})'
                        matches.append(RuleMatch(path, message.format(len(allowed_value), value_limit)))

        return matches
