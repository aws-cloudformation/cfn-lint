"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
#pylint: disable=cyclic-import
import cfnlint.rules

OPERATOR = [
    'EQUALS',
    'NOT_EQUALS',
    '==',
    '!=',
    'IN',
    'NOT_IN',
    '>=',
    '<=']


def CreateCustomRule(rule_id, resourceType, prop, value, error_message, description, shortdesc, rule_func):

    class CustomRule(cfnlint.rules.CloudFormationLintRule):

        def __init__(self, rule_id, resourceType, prop, value, error_message, description, shortdesc, rule_func):
            super(CustomRule, self).__init__()
            self.resource_property_types.append(resourceType)
            self.id = rule_id
            self.property_chain = prop.split('.')
            self.property_value = value
            self.error_message = error_message
            self.description = description
            self.shortdesc = shortdesc
            self.rule_func = rule_func

        def _remaining_inset_properties(self, property_chain):
            if len(property_chain) > 1:
                return property_chain[1:]

            return []

        def _check_value(self, value, path, property_chain, cfn):
            matches = []
            if property_chain:
                new_property_chain = self._remaining_inset_properties(property_chain)
                matches.extend(
                    cfn.check_value(
                        value, property_chain[0], path,
                        check_value=self._check_value,
                        property_chain=new_property_chain,
                        cfn=cfn,
                    ))
                return matches
            if value is not None:
                matches.extend(self.rule_func(value, self.property_value, path))
            return matches

        def match_resource_properties(self, properties, _, path, cfn):
            new_property_chain = self._remaining_inset_properties(self.property_chain)
            return cfn.check_value(
                properties, self.property_chain[0], path,
                check_value=self._check_value,
                property_chain=new_property_chain,
                cfn=cfn,
            )

    return CustomRule(rule_id, resourceType, prop, value, error_message, description, shortdesc, rule_func)


def CreateEqualsRule(rule_id, resourceType, prop, value, error_message):
    def rule_func(value, expected_value, path):
        matches = []
        if str(value).strip().lower() != str(expected_value).strip().lower():
            matches.append(cfnlint.rules.RuleMatch(
                path, error_message or 'Must equal check failed'))

        return matches

    return CreateCustomRule(
        rule_id, resourceType, prop, value, error_message,
        shortdesc='Custom rule to check for equal values',
        description='Created from the custom rules parameter. This rule will check if a property value is equal to the specified value.',
        rule_func=rule_func,
    )


def CreateNotEqualsRule(rule_id, resourceType, prop, value, error_message):
    def rule_func(value, expected_values, path):
        matches = []
        if str(value).strip().lower() == str(expected_values).strip().lower():
            matches.append(cfnlint.rules.RuleMatch(
                path, error_message or 'Must not equal check failed'))

        return matches

    return CreateCustomRule(
        rule_id, resourceType, prop, value, error_message,
        shortdesc='Custom rule to check for not equal values',
        description='Created from the custom rules parameter. This rule will check if a property value is NOT equal to the specified value.',
        rule_func=rule_func,
    )


def CreateGreaterRule(rule_id, resourceType, prop, value, error_message):
    def rule_func(value, expected_value, path):
        matches = []
        if checkInt(value.strip()) and checkInt(str(expected_value).strip()):
            if value.strip().lower() < str(expected_value).strip().lower():
                matches.append(cfnlint.rules.RuleMatch(
                    path, error_message or 'Greater than check failed'))
        else:
            matches.append(cfnlint.rules.RuleMatch(
                path, error_message or 'Given values are not numeric'))

        return matches

    return CreateCustomRule(
        rule_id, resourceType, prop, value, error_message,
        shortdesc='Custom rule to check for if a value is greater than the specified value',
        description='Created from the custom rules parameter. This rule will check if a property value is greater than the specified value.',
        rule_func=rule_func,
    )


def CreateLesserRule(rule_id, resourceType, prop, value, error_message):
    def rule_func(value, expected_value, path):
        matches = []
        if checkInt(value.strip()) and checkInt(str(expected_value).strip()):
            if value.strip().lower() > str(expected_value).strip().lower():
                matches.append(cfnlint.rules.RuleMatch(
                    path, error_message or 'Lesser than check failed'))
        else:
            matches.append(cfnlint.rules.RuleMatch(
                path, error_message or 'Given values are not numeric'))

        return matches

    return CreateCustomRule(
        rule_id, resourceType, prop, value, error_message,
        shortdesc='Custom rule to check for if a value is lesser than the specified value',
        description='Created from the custom rules parameter. This rule will check if a property value is lesser than the specified value.',
        rule_func=rule_func,
    )


def CreateInSetRule(rule_id, resourceType, prop, value, error_message):
    def rule_func(value, expected_values, path):
        matches = []
        if value not in expected_values:
            matches.append(cfnlint.rules.RuleMatch(path, error_message or 'In set check failed'))

        return matches

    return CreateCustomRule(
        rule_id, resourceType, prop, value, error_message,
        shortdesc='Custom rule to check for if a value exists in a list of specified values',
        description='Created from the custom rules parameter. This rule will check if a property value exists inside a list of specified values.',
        rule_func=rule_func,
    )


def CreateNotInSetRule(rule_id, resourceType, prop, value, error_message):
    def rule_func(value, expected_values, path):
        matches = []
        if value in expected_values:
            matches.append(cfnlint.rules.RuleMatch(
                path, error_message or 'Not in set check failed'))

        return matches

    return CreateCustomRule(
        rule_id, resourceType, prop, value, error_message,
        shortdesc='Custom rule to check for if a value does not exist in a list of specified values',
        description='Created from the custom rules parameter. This rule will check if a property value does not exist inside a list of specified values.',
        rule_func=rule_func,
    )


def CreateInvalidRule(rule_id, operator):
    class InvalidRule(cfnlint.rules.CloudFormationLintRule):

        def __init__(self, rule_id, operator):
            super(InvalidRule, self).__init__()
            self.id = rule_id
            self.operator = operator
            self.description = 'Created from the custom rule parameter. This rule is the result of an invalid configuration of a custom rule.'
            self.shortdesc = 'Invalid custom rule configuration'

        def match(self, _):
            message = '"{0}" not in supported operators: [{1}]'
            return [
                cfnlint.rules.RuleMatch(
                    [], message.format(str(self.operator), ', '.join(OPERATOR)))
            ]

    return InvalidRule(rule_id, operator)


def checkInt(i):
    """ Python 2.7 Compatibility - There is no isnumeric() method """
    try:
        int(i)
        return True
    except ValueError:
        return False
