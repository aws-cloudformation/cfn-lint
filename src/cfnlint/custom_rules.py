"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
# pylint: disable=W0108
# pylint: disable=W0622
# pylint: disable=W0603

import logging
import cfnlint
import cfnlint.runner
import cfnlint.rules.custom.Operators
import cfnlint.rules.custom.Rule

LOGGER = logging.getLogger(__name__)
CUSTOM_RULES_FILE = None
Operator = {'EQUALS': lambda x, y, z: cfnlint.rules.custom.Operators.equalsOp(x, y, z),
            'NOT_EQUALS': lambda x, y, z: cfnlint.rules.custom.Operators.notEqualsOp(x, y, z),
            '==': lambda x, y, z: cfnlint.rules.custom.Operators.equalsOp(x, y, z),
            '!=': lambda x, y, z: cfnlint.rules.custom.Operators.notEqualsOp(x, y, z),
            'IN': lambda x, y, z: cfnlint.rules.custom.Operators.InSetOp(x, y, z),
            'NOT_IN': lambda x, y, z: cfnlint.rules.custom.Operators.NotInSetOp(x, y, z),
            '>=': lambda x, y, z: cfnlint.rules.custom.Operators.greaterOp(x, y, z),
            '<=': lambda x, y, z: cfnlint.rules.custom.Operators.lessOp(x, y, z)}

def check(template, rules, runner):
    """ Process custom rule file """
    matches = []

    if CUSTOM_RULES_FILE is None:
        return matches

    try:
        with open(CUSTOM_RULES_FILE) as customRules:
            line_number = 1
            for line in customRules:
                LOGGER.debug('Processing Custom Rule Line %d', line_number)
                rule = cfnlint.rules.custom.Rule.make_rule(line, line_number)
                if rule.valid and rule.resourceType[0] != '#':
                    try:
                        resource_properties = template.get_resource_properties([rule.resourceType])
                        operator_result = Operator[rule.operator](template, rule, resource_properties)
                        matches += operator_result
                    except KeyError:
                        matches.append(cfnlint.rules.Match(
                            1, 1,
                            1, 1,
                            template.filename, cfnlint.rules.custom.Operators.CustomRule('E9999', 'Error'),
                            str(rule.operator) + ' not in supported operators: ' + str(list(Operator.keys())) + ' at ' + str(line), None))
                line_number += 1
        arg_matches = []
        for match in matches:
            if rules.is_rule_enabled(match.rule.id, False):
                arg_matches.append(match)
        return runner.check_metadata_directives(arg_matches)

    except EnvironmentError:
        LOGGER.error('Could not find custom rule file: %s', str(CUSTOM_RULES_FILE))
    return matches

def set_filename(filename):
    global CUSTOM_RULES_FILE
    if isinstance(filename, list):
        filename = filename[0]
    CUSTOM_RULES_FILE = filename
