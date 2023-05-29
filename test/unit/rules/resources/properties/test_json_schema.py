"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase
from typing import List
from unittest.mock import Mock

from cfnlint.decode.cfn_json import Mark
from cfnlint.decode.node import str_node
from cfnlint.rules import RuleMatch
from cfnlint.rules.resources.properties import AllowedPattern as RuleStringPattern
from cfnlint.rules.resources.properties import AllowedValue as RuleAllowedValue
from cfnlint.rules.resources.properties import ListDuplicates as RuleListDuplicates
from cfnlint.rules.resources.properties import ListSize as RuleListSize
from cfnlint.rules.resources.properties import NumberSize as RuleNumberSize
from cfnlint.rules.resources.properties import OnlyOne as RuleOneOf
from cfnlint.rules.resources.properties import Properties as RuleProperties
from cfnlint.rules.resources.properties import Required as RuleRequired
from cfnlint.rules.resources.properties import StringSize as RuleStringSize
from cfnlint.rules.resources.properties import ValuePrimitiveType as RuleType
from cfnlint.rules.resources.properties.JsonSchema import (  # pylint: disable=E0401
    JsonSchema,
)


class TestJsonSchema(BaseRuleTestCase):
    """Test Json Size"""

    def setUp(self):
        """Setup"""
        super(TestJsonSchema, self).setUp()
        self.rule = JsonSchema()
        self.table = {
            build_key("A"): [{"AttributeName": "pk", "KeyType": "HASH"}],
            build_key("B"): {
                build_key("C"): "TTL",
                build_key("D"): True,
            },
            build_key("E"): "string",
            build_key("F"): 5,
            build_key("G"): ["A", "A"],
        }
        self.ruleset = self.rule.rule_set.copy()

        self.rule.child_rules = {
            "E3002": RuleProperties.Properties(),
            "E3003": RuleRequired.Required(),
            "E3012": RuleType.ValuePrimitiveType(),
            "E3030": RuleAllowedValue.AllowedValue(),
            "E3031": RuleStringPattern.AllowedPattern(),
            "E3032": RuleListSize.ListSize(),
            "E3033": RuleStringSize.StringSize(),
            "E3034": RuleNumberSize.NumberSize(),
            "E3037": RuleListDuplicates.ListDuplicates(),
            "E2523": RuleOneOf.OnlyOne(),
        }
        self.cfn = Mock()
        self.cfn.get_valid_refs = {}
        self.path = ["Resources", "Table", "Properties"]

    def build_result(
        self, rule_id: str, message: str, path: List[str], **kwargs
    ) -> RuleMatch:
        return RuleMatch(
            self.path + path[:],
            message,
            rule=self.rule.child_rules.get(rule_id),
            location=(
                f"{path[-1]}-sm-line",
                f"{path[-1]}-sm-column",
                f"{path[-1]}-em-line",
                f"{path[-1]}-em-column",
            ),
            **kwargs,
        )

    def validate(self, schema, expected, object=None):
        validator = self.rule.setup_validator(schema=schema)
        if object is None:
            object = self.table

        matches = self.rule.json_schema_validate(validator, object, self.path)

        self.assertListEqual(list(map(vars, expected)), list(map(vars, matches)))

    def test_required_empty(self):
        schema = {
            "properties": {
                "A": {
                    "type": "string",
                },
            },
            "required": ["A"],
        }

        expected = [
            RuleMatch(
                self.path,
                "'A' is a required property",
                rule=self.rule.child_rules.get("E3003"),
            )
        ]

        self.validate(schema, expected, {})

    def test_required_nested(self):
        schema = {
            "definitions": {
                "Z": {
                    "type": "object",
                    "properties": {
                        "X": {
                            "type": "string",
                        },
                    },
                    "required": ["X"],
                },
            },
            "properties": {
                "B": {"$ref": "#/definitions/Z"},
            },
            "required": ["B"],
        }

        expected = [
            self.build_result("E3003", "'X' is a required property", ["B"]),
        ]

        self.validate(schema, expected)

    def test_additional_properties(self):
        schema = {
            "definitions": {
                "Z": {
                    "type": "object",
                    "properties": {
                        "C": {
                            "type": "string",
                        }
                    },
                    "additionalProperties": False,
                }
            },
            "properties": {
                "A": {
                    "type": "array",
                },
                "B": {"$ref": "#/definitions/Z"},
                "F": {"type": "number"},
                "G": {"type": "array"},
            },
            "additionalProperties": False,
        }

        expected = [
            self.build_result(
                "E3002",
                "Additional properties are not allowed (D unexpected)",
                ["B", "D"],
            ),
            self.build_result(
                "E3002", "Additional properties are not allowed (E unexpected)", ["E"]
            ),
        ]

        self.validate(schema, expected)

    def test_one_of(self):
        schema = {
            "definitions": {
                "Z": {
                    "oneOf": [
                        {
                            "type": "object",
                            "properties": {
                                "C": {
                                    "type": "string",
                                }
                            },
                            # there are additional properties
                            "additionalProperties": False,
                        },
                        {
                            "type": "object",
                            "properties": {
                                # Z doesn't exist
                                "Z": {
                                    "type": "string",
                                }
                            },
                            "required": ["Z"],
                        },
                    ]
                }
            },
            "properties": {
                "B": {"$ref": "#/definitions/Z"},
            },
        }

        expected = [
            self.build_result(
                "E2523",
                "{'C': 'TTL', 'D': True} is not valid under any of the given schemas",
                ["B"],
            ),
        ]

        self.validate(schema, expected)

    def test_pattern(self):
        schema = {
            "properties": {
                "E": {"type": "string", "pattern": "^number$"},
            },
        }

        expected = [
            self.build_result("E3031", "'string' does not match '^number$'", ["E"]),
        ]

        self.validate(schema, expected)

    def test_min_items(self):
        schema = {
            "properties": {
                "A": {
                    "type": "array",
                    "minItems": 5,
                },
            },
        }

        expected = [
            self.build_result(
                "E3032",
                "[{'AttributeName': 'pk', 'KeyType': 'HASH'}] is too short",
                ["A"],
            ),
        ]

        self.validate(schema, expected)

    def test_max_items(self):
        schema = {
            "properties": {
                "A": {
                    "type": "array",
                    "maxItems": 0,
                },
            },
        }

        expected = [
            self.build_result(
                "E3032",
                "[{'AttributeName': 'pk', 'KeyType': 'HASH'}] is too long",
                ["A"],
            ),
        ]

        self.validate(schema, expected)

    def test_min_number(self):
        schema = {
            "properties": {
                "F": {
                    "type": "number",
                    "minimum": 6,
                },
            },
        }

        expected = [
            self.build_result("E3034", "5 is less than the minimum of 6", ["F"]),
        ]

        self.validate(schema, expected)

    def test_max_number(self):
        schema = {
            "properties": {
                "F": {
                    "type": "number",
                    "maximum": 4,
                },
            },
        }

        expected = [
            self.build_result("E3034", "5 is greater than the maximum of 4", ["F"]),
        ]

        self.validate(schema, expected)

    def test_exclusive_min_number(self):
        schema = {
            "properties": {
                "F": {
                    "type": "number",
                    "minimum": 6,
                },
            },
        }

        expected = [
            self.build_result("E3034", "5 is less than the minimum of 6", ["F"]),
        ]

        self.validate(schema, expected)

    def test_exclusive_max_number(self):
        schema = {
            "properties": {
                "F": {
                    "type": "number",
                    "maximum": 4,
                },
            },
        }

        expected = [
            self.build_result("E3034", "5 is greater than the maximum of 4", ["F"]),
        ]

        self.validate(schema, expected)

    def test_unique_array(self):
        schema = {
            "properties": {
                "G": {
                    "type": "array",
                    "uniqueItems": True,
                },
            },
        }

        expected = [
            self.build_result("E3037", "['A', 'A'] has non-unique elements", ["G"]),
        ]

        self.validate(schema, expected)

    def test_min_length(self):
        schema = {
            "properties": {
                "E": {
                    "type": "string",
                    "minLength": 10,
                },
            },
        }

        expected = [
            self.build_result("E3033", "'string' is too short", ["E"]),
        ]

        self.validate(schema, expected)

    def test_max_length(self):
        schema = {
            "properties": {
                "E": {
                    "type": "string",
                    "maxLength": 3,
                },
            },
        }

        expected = [
            self.build_result("E3033", "'string' is too long", ["E"]),
        ]

        self.validate(schema, expected)

    def test_enum(self):
        schema = {
            "properties": {
                "E": {"type": "string", "enum": ["number"]},
            },
        }

        expected = [
            self.build_result("E3030", "'string' is not one of ['number']", ["E"]),
        ]

        self.validate(schema, expected)

    def test_type(self):
        schema = {
            "properties": {
                "E": {
                    "type": "array",
                },
            },
        }

        expected = [
            self.build_result(
                "E3012",
                "'string' is not of type 'array'",
                ["E"],
                actual_type="str",
                expected_type="'array'",
            ),
        ]

        self.validate(schema, expected)


def build_key(key: str):
    caps = []
    for s in key:
        if s.isupper():
            caps.append(s)
    abbr = "".join(caps)
    return str_node(
        key,
        Mark(f"{abbr}-sm-line", f"{abbr}-sm-column"),
        Mark(f"{abbr}-em-line", f"{abbr}-em-column"),
    )
