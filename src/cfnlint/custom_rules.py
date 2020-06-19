"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
# pylint: disable=W0108
# pylint: disable=W0622

import logging
import cfnlint
import cfnlint.runner
import cfnlint.customRules.Operators
import cfnlint.customRules.Rule

LOGGER = logging.getLogger(__name__)
Operator = {'EQUALS': lambda x, y, z: cfnlint.customRules.Operators.equalsOp(x, y, z),
            'NOT_EQUALS': lambda x, y, z: cfnlint.customRules.Operators.notEqualsOp(x, y, z),
            '==': lambda x, y, z: cfnlint.customRules.Operators.equalsOp(x, y, z),
            '!=': lambda x, y, z: cfnlint.customRules.Operators.notEqualsOp(x, y, z),
            'IN': lambda x, y, z: cfnlint.customRules.Operators.InSetOp(x, y, z),
            'NOT_IN': lambda x, y, z: cfnlint.customRules.Operators.NotInSetOp(x, y, z),
            '>=': lambda x, y, z: cfnlint.customRules.Operators.greaterOp(x, y, z),
            '<=': lambda x, y, z: cfnlint.customRules.Operators.lessOp(x, y, z)}

def check(filename, template, rules, runner):
    """ Process custom rule file """
    matches = []

    with open(filename) as customRules:
        line_number = 1
        for line in customRules:
            LOGGER.debug('Processing Custom Rule Line %d', line_number)
            rule = cfnlint.customRules.Rule.make_rule(line, line_number)
            if rule.valid and rule.resourceType[0] != '#':
                try:
                    resource_properties = template.get_resource_properties([rule.resourceType])
                    operator_result = Operator[rule.operator](template, rule, resource_properties)
                    matches += operator_result
                except KeyError:
                    matches.append(cfnlint.rules.Match(
                        1, 1,
                        1, 1,
                        template.filename, cfnlint.customRules.Operators.CustomRule('E9999', 'Error'),
                        str(rule.operator) + ' not in supported operators: ' + str(list(Operator.keys())) + ' at ' + str(line), None))
            line_number += 1
    arg_matches = []
    for match in matches:
        if rules.is_rule_enabled(match.rule.id, False):
            arg_matches.append(match)
    return runner.check_metadata_directives(arg_matches)
