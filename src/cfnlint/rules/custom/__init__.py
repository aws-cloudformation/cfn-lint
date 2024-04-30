"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

# pylint: disable=cyclic-import
import json

import cfnlint.rules.custom.Operators


# pylint: disable=too-many-return-statements
def make_rule(line, lineNumber):
    """Object Maker Function"""

    def get_value(value):
        raw_value = value.strip()
        try:
            return json.loads(raw_value)
        except ValueError:
            return raw_value

    def set_arguments(argument, error):
        raw_value = argument.split(error)
        value = process_sets(raw_value[0])
        error_message = None
        if len(raw_value) > 1:
            error_message = raw_value[1].strip().strip('"')
        return value, error_message

    def process_sets(raw_value):
        if (
            len(raw_value) > 1
            and raw_value[0] == "["
            and (raw_value[-2] == "]" or raw_value[-1] == "]")
        ):
            raw_value = raw_value[1:-2]
            raw_value = raw_value.split(",")
            for x in raw_value:
                x = x.strip()
            return raw_value

        return raw_value

    line = line.rstrip()
    # check line is not a comment or empty line
    if not line.startswith("#") and line != "":
        rule_id = lineNumber + 9000
        line = line.split(" ", 3)
        error_level = "E"
        if len(line) == 4:
            resourceType = line[0]
            prop = line[1]
            operator = line[2]
            value = None
            error_message = None
            if "WARN" in line[3]:
                error_level = "W"
                value, error_message = set_arguments(line[3], "WARN")
            elif "ERROR" in line[3]:
                error_level = "E"
                value, error_message = set_arguments(line[3], "ERROR")
            else:
                value = process_sets(line[3])
                value = get_value(line[3])

            if isinstance(value, str):
                value = value.strip().strip('"')

            if operator in ["EQUALS", "=="]:
                return cfnlint.rules.custom.Operators.CreateEqualsRule(
                    error_level + str(rule_id), resourceType, prop, value, error_message
                )
            if operator in ["NOT_EQUALS", "!="]:
                return cfnlint.rules.custom.Operators.CreateNotEqualsRule(
                    error_level + str(rule_id), resourceType, prop, value, error_message
                )
            if operator == "REGEX_MATCH":
                return cfnlint.rules.custom.Operators.CreateRegexMatchRule(
                    error_level + str(rule_id), resourceType, prop, value, error_message
                )
            if operator == "IN":
                return cfnlint.rules.custom.Operators.CreateInSetRule(
                    error_level + str(rule_id), resourceType, prop, value, error_message
                )
            if operator == "NOT_IN":
                return cfnlint.rules.custom.Operators.CreateNotInSetRule(
                    error_level + str(rule_id), resourceType, prop, value, error_message
                )
            if operator == ">":
                return cfnlint.rules.custom.Operators.CreateGreaterRule(
                    error_level + str(rule_id), resourceType, prop, value, error_message
                )
            if operator == ">=":
                return cfnlint.rules.custom.Operators.CreateGreaterEqualRule(
                    error_level + str(rule_id), resourceType, prop, value, error_message
                )
            if operator == "<":
                return cfnlint.rules.custom.Operators.CreateLesserRule(
                    error_level + str(rule_id), resourceType, prop, value, error_message
                )
            if operator == "<=":
                return cfnlint.rules.custom.Operators.CreateLesserEqualRule(
                    error_level + str(rule_id), resourceType, prop, value, error_message
                )
            if operator == "IS":
                if value in ["DEFINED", "NOT_DEFINED"]:
                    return cfnlint.rules.custom.Operators.CreateCustomIsDefinedRule(
                        error_level + str(rule_id),
                        resourceType,
                        prop,
                        value,
                        error_message,
                    )
                return cfnlint.rules.custom.Operators.CreateInvalidRule(
                    "E" + str(rule_id), f"{operator} {value}"
                )

        return cfnlint.rules.custom.Operators.CreateInvalidRule(
            "E" + str(rule_id), operator
        )
