"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from unittest import TestCase

from cfnlint.context import Context
from cfnlint.jsonschema import StandardValidator, ValidationError
from cfnlint.rules.jsonschema.Base import BaseJsonSchema


class Rule(BaseJsonSchema):
    def __init__(self):
        """Init"""
        super().__init__()
        self.rule_set = {"enum": "E3003", "pattern": "E3004"}
        self.child_rules = dict.fromkeys(list(self.rule_set.values()))


class ReturnRule(BaseJsonSchema):
    id = "E3005"


class EnumRule(BaseJsonSchema):
    id = "E3003"

    def __init__(self) -> None:
        super().__init__()
        self.rule = ReturnRule()

    def enum(self, validator, enums, instance, schema):
        yield ValidationError("test", rule=self.rule)


class PatternRule(BaseJsonSchema):
    id = "E3004"

    def pattern(self, validator, ptrn, instance, schema):
        yield ValidationError("test")


class TestBaseJsonSchema(TestCase):
    """Test Base JSON Schema validation"""

    def setUp(self) -> None:
        super().setUp()
        self.rule = Rule()

    def test_rule_disabled(self):
        schema = {
            "type": "string",
            "enum": ["foo"],
        }
        validator = self.rule.extend_validator(
            validator=StandardValidator({}),
            schema=schema,
            context=Context(),
        )

        self.assertEqual(self.rule.json_schema_validate(validator, "bar", []), [])

    def test_rule_enabled(self):
        schema = {
            "type": "string",
            "pattern": "foo",
        }
        self.rule.child_rules["E3004"] = PatternRule()
        validator = self.rule.extend_validator(
            validator=StandardValidator({}),
            schema=schema,
            context=Context(),
        )

        self.assertEqual(
            len(list(self.rule.json_schema_validate(validator, "bar", []))), 1
        )
        self.assertEqual(
            list(self.rule.json_schema_validate(validator, "bar", []))[0].rule.id,
            "E3004",
        )

    def test_rule_passed_in_validation_error(self):
        schema = {
            "type": "string",
            "enum": ["foo"],
        }
        self.rule.child_rules["E3003"] = EnumRule()
        validator = self.rule.extend_validator(
            validator=StandardValidator({}),
            schema=schema,
            context=Context(),
        )

        self.assertEqual(
            list(self.rule.json_schema_validate(validator, "bar", []))[0].rule.id,
            "E3005",
        )
