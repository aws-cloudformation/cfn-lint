"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import logging

import regex as re
import yaml

import cfnlint.rules
import cfnlint.rules.custom
import cfnlint.rules.custom.Operators

LOGGER = logging.getLogger(__name__)

Operators = {
    "EQUALS": lambda value, expected_value: str(value).strip().lower()
    == str(expected_value).strip().lower(),
    "NOT_EQUALS": lambda value, expected_value: str(value).strip().lower()
    != str(expected_value).strip().lower(),
    "==": lambda value, expected_value: str(value).strip().lower()
    == str(expected_value).strip().lower(),
    "!=": lambda value, expected_value: str(value).strip().lower()
    != str(expected_value).strip().lower(),
    ">": lambda value, expected_value: str(value).strip().isnumeric()
    and str(expected_value).strip().isnumeric()
    and float(value) > float(expected_value),
    ">=": lambda value, expected_value: str(value).strip().isnumeric()
    and str(expected_value).strip().isnumeric()
    and float(value) >= float(expected_value),
    "<": lambda value, expected_value: str(value).strip().isnumeric()
    and str(expected_value).strip().isnumeric()
    and float(value) < float(expected_value),
    "<=": lambda value, expected_value: str(value).strip().isnumeric()
    and str(expected_value).strip().isnumeric()
    and float(value) <= float(expected_value),
    "IN": lambda value, expected_values: str(value).strip().lower()
    in [str(i).strip().lower() for i in expected_values],
    "NOT_IN": lambda value, expected_values: str(value).strip().lower()
    not in [str(i).strip().lower() for i in expected_values],
    "IS": lambda value, expected_value: (
        expected_value == "DEFINED" and value is not None
    )
    or (expected_value == "NOT_DEFINED" and value is None),
    "REGEX_MATCH": lambda value, pattern: re.match(pattern, value),
}

CreateRuleFromOp = {
    "EQUALS": cfnlint.rules.custom.Operators.CreateEqualsRule,
    "NOT_EQUALS": cfnlint.rules.custom.Operators.CreateNotEqualsRule,
    "==": cfnlint.rules.custom.Operators.CreateEqualsRule,
    "!=": cfnlint.rules.custom.Operators.CreateNotEqualsRule,
    ">": cfnlint.rules.custom.Operators.CreateGreaterRule,
    ">=": cfnlint.rules.custom.Operators.CreateGreaterEqualRule,
    "<": cfnlint.rules.custom.Operators.CreateLesserRule,
    "<=": cfnlint.rules.custom.Operators.CreateLesserEqualRule,
    "IN": cfnlint.rules.custom.Operators.CreateInSetRule,
    "NOT_IN": cfnlint.rules.custom.Operators.CreateNotInSetRule,
    "IS": cfnlint.rules.custom.Operators.CreateCustomIsDefinedRule,
    "REGEX_MATCH": cfnlint.rules.custom.Operators.CreateRegexMatchRule,
}


def flatten(x):
    for el in x:
        if isinstance(el, list):
            yield from flatten(el)
        else:
            yield el


class MatchProjectValidateRule(cfnlint.rules.CloudFormationLintRule):
    def __init__(
        self,
        rule_id=None,
        rule_definition=None,
    ):
        super().__init__()
        if rule_id is None and rule_definition is None:
            self.do_nothing = True
            return
        self.do_nothing = False
        self.id = rule_id
        if isinstance(rule_definition, str):
            rule_definition = yaml.safe_load(rule_definition)
        self.config = rule_definition
        self.resource_types = (
            self.config["ResourceTypes"]
            if isinstance(self.config["ResourceTypes"], list)
            else [self.config["ResourceTypes"]]
        )
        self.resource_property_types.extend(self.resource_types)
        self.error_message = self.config["ErrorMessage"]
        self.shortdesc = self.config.get("ShortDescription", f"{self.id}")
        self.description = self.config.get("Description", f"{self.shortdesc}")
        for resource_type in self.resource_types:
            LOGGER.debug("%s:%s:%s initialized", self.id, resource_type, self.shortdesc)

    def _extract_path_value(self, resource_properties, path):
        if path == "":
            return True, resource_properties
        path_parts = path.split(".")
        current = resource_properties
        for part in path_parts:
            if part not in current:
                return False, None
            current = current[part]
        return True, current

    def _check_condition(self, resource_properties, condition):
        op = list(condition.keys())[0]
        [path, expected_value] = condition[op]
        op = op[4:]
        LOGGER.debug("Checking condition %s %s %s", path, op, expected_value)
        path_exists, value = self._extract_path_value(resource_properties, path)
        # behavior is same comp. to custom rule, i.e. rule does nothing if path does not exist
        # unless explicitly requiring it to be undefined
        if not path_exists and op != "IS" and expected_value != "NOT_DEFINED":
            return False
        return Operators[op](value, expected_value)

    def _check_conditions(self, resource_properties):
        if isinstance(self.config["Conditions"], list):
            LOGGER.debug("Has %d conditions", len(self.config["Conditions"]))
            return all(
                self._check_condition(resource_properties, condition)
                for condition in self.config["Conditions"]
            )

        LOGGER.debug("Has 1 conditions")
        return self._check_condition(resource_properties, self.config["Conditions"])

    def _project_value(self, value, path_split):
        if (len(path_split) == 0) or (value is None):
            return value
        k, next_path_split = path_split[0], path_split[1:]
        v = value.get(k, None)
        if isinstance(v, list):
            return [self._project_value(item, next_path_split) for item in v]
        return self._project_value(v, next_path_split)

    def _compute_projection(self, resource_properties):
        if self.config["Projection"] is not None:
            return list(
                flatten(
                    self._project_value(
                        resource_properties, self.config["Projection"].split(".")
                    )
                )
            )
        return None

    def _match_resource_properties(
        self, resource_properties, property_type, path, cfn, projected_values
    ):
        matches = []
        validations = (
            self.config["Validations"]
            if isinstance(self.config["Validations"], list)
            else [self.config["Validations"]]
        )
        for validation in validations:
            op = list(validation.keys())[0]
            [validation_path, expected_value] = validation[op]
            op = op[4:]
            if expected_value == "Fn::Projection":
                expected_value = projected_values
            try:
                rule_instance = CreateRuleFromOp[op](
                    self.id,
                    property_type,
                    validation_path,
                    expected_value,
                    self.error_message,
                )
                rule_matches = rule_instance.match_resource_properties(
                    resource_properties, property_type, path, cfn
                )
                matches.extend(rule_matches)
            except KeyError:
                matches.extend(
                    cfnlint.rules.custom.Operators.CreateInvalidRule(self.id, op).match(
                        cfn
                    )
                )
        return matches

    def match_resource_properties(self, resource_properties, property_type, path, cfn):
        LOGGER.debug(
            "Linting %s on %s::%s", self.id, property_type, str.join(".", path[:2])
        )
        if self.config.get("Conditions", None) is not None:
            condition = self._check_conditions(resource_properties)
            LOGGER.debug("Condition %s", condition)
            if not condition:
                return []

        if self.config.get("Projection", None) is not None:
            projected_values = self._compute_projection(resource_properties)
            LOGGER.debug("Projected values %s", projected_values)
        else:
            projected_values = None

        return self._match_resource_properties(
            resource_properties, property_type, path, cfn, projected_values
        )
