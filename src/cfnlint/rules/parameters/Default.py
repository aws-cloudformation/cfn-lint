"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import re
import six
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class Default(CloudFormationLintRule):
    """Check if Parameters are configured correctly"""
    id = 'E2015'
    shortdesc = 'Default value is within parameter constraints'
    description = 'Making sure the parameters have a default value inside AllowedValues, MinValue, MaxValue, AllowedPattern'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/parameters-section-structure.html'
    tags = ['parameters']

    def check_allowed_pattern(self, allowed_value, allowed_pattern, path):
        """
            Check allowed value against allowed pattern
        """
        message = 'Default should be allowed by AllowedPattern'
        try:
            if not re.match(allowed_pattern, str(allowed_value)):
                return([RuleMatch(path, message)])
        except re.error as ex:
            self.logger.debug('Regex pattern "%s" isn\'t supported by Python: %s',
                              allowed_pattern, ex)

        return []

    def check_min_value(self, allowed_value, min_value, path):
        """
            Check allowed value against min value
        """
        message = 'Default should be equal to or higher than MinValue'

        if isinstance(allowed_value, six.integer_types) and isinstance(min_value, six.integer_types):
            if allowed_value < min_value:
                return([RuleMatch(path, message)])

        return []

    def check_max_value(self, allowed_value, max_value, path):
        """
            Check allowed value against max value
        """
        message = 'Default should be less than or equal to MaxValue'

        if isinstance(allowed_value, six.integer_types) and isinstance(max_value, six.integer_types):
            if allowed_value > max_value:
                return([RuleMatch(path, message)])

        return []

    def check_allowed_values(self, allowed_value, allowed_values, path):
        """
            Check allowed value against allowed values
        """
        message = 'Default should be a value within AllowedValues'

        if allowed_value not in allowed_values:
            return([RuleMatch(path, message)])

        return []

    def check_min_length(self, allowed_value, min_length, path):
        """
            Check allowed value against MinLength
        """
        message = 'Default should have a length above or equal to MinLength'

        value = allowed_value if isinstance(allowed_value, six.string_types) else str(allowed_value)
        if isinstance(min_length, six.integer_types):
            if len(value) < min_length:
                return([RuleMatch(path, message)])

        return []

    def check_max_length(self, allowed_value, max_length, path):
        """
            Check allowed value against MaxLength
        """
        message = 'Default should have a length below or equal to MaxLength'

        value = allowed_value if isinstance(allowed_value, six.string_types) else str(allowed_value)
        if isinstance(max_length, six.integer_types):
            if len(value) > max_length:
                return([RuleMatch(path, message)])

        return []

    def match(self, cfn):
        matches = []

        for paramname, paramvalue in cfn.get_parameters().items():
            default_value = paramvalue.get('Default')
            if default_value is not None:
                path = ['Parameters', paramname, 'Default']
                allowed_pattern = paramvalue.get('AllowedPattern')
                if allowed_pattern:
                    matches.extend(
                        self.check_allowed_pattern(
                            default_value, allowed_pattern, path
                        )
                    )
                min_value = paramvalue.get('MinValue')
                if min_value:
                    matches.extend(
                        self.check_min_value(
                            default_value, min_value, path
                        )
                    )
                max_value = paramvalue.get('MaxValue')
                if max_value is not None:
                    matches.extend(
                        self.check_max_value(
                            default_value, max_value, path
                        )
                    )
                allowed_values = paramvalue.get('AllowedValues')
                if allowed_values:
                    matches.extend(
                        self.check_allowed_values(
                            default_value, allowed_values, path
                        )
                    )
                min_length = paramvalue.get('MinLength')
                if min_length is not None:
                    matches.extend(
                        self.check_min_length(
                            default_value, min_length, path
                        )
                    )
                max_length = paramvalue.get('MaxLength')
                if max_length is not None:
                    matches.extend(
                        self.check_max_length(
                            default_value, max_length, path
                        )
                    )

        return matches
