"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.unit.rules import BaseRuleTestCase

from jsonschema import Draft7Validator

from cfnlint.rules.resources.properties.Properties import (
    Properties,  # pylint: disable=E0401
)


class TestAdditionalProperties(BaseRuleTestCase):
    """Test Allowed Value Property Configuration"""

    def test_properties(self):
        """Test Properties"""
        rule = Properties()
        validator = Draft7Validator({})

        base_object = {
            "a": "a",
            "b": "b",
        }

        schema = {
            "type": "object",
            "properties": {
                "a": {"type": "string"},
                "b": {"type": "string"},
            },
            "additionalProperties": False,
        }

        self.assertEqual(
            len(
                list(
                    rule.properties(
                        validator,
                        schema,
                        {
                            "Fn::If": [
                                "Condition",
                                {**base_object},
                                {**base_object},
                            ]
                        },
                        schema,
                    )
                )
            ),
            0,
        )

        self.assertEqual(
            len(
                list(
                    rule.properties(
                        validator,
                        schema,
                        {
                            "Fn::If": [
                                "Condition",
                                base_object,
                                {**base_object, **{"c": "c"}},
                            ]
                        },
                        schema,
                    )
                )
            ),
            1,
        )

        self.assertEqual(
            len(
                list(
                    rule.properties(
                        validator,
                        schema,
                        "test",
                        schema,
                    )
                )
            ),
            0,
        )

        self.assertEqual(
            len(
                list(
                    rule.properties(
                        validator,
                        schema,
                        {
                            "Fn::If": [
                                "Condition",
                                base_object,
                                base_object,
                                {**base_object, **{"c": "c"}},
                            ]
                        },
                        schema,
                    )
                )
            ),
            0,
        )

        self.assertEqual(
            len(
                list(
                    rule.properties(
                        validator,
                        schema,
                        {"Fn::If": {"foo": "bar"}},
                        schema,
                    )
                )
            ),
            0,
        )

    def test_additional_properties(self):
        """Test Positive"""
        rule = Properties()
        validator = Draft7Validator({})

        base_object = {
            "a": "a",
            "b": "b",
        }

        schema = {
            "type": "object",
            "properties": {
                "a": {"type": "string"},
                "b": {"type": "string"},
            },
        }

        self.assertEqual(
            len(
                list(
                    rule.additionalProperties(
                        validator,
                        False,
                        base_object,
                        schema,
                    )
                )
            ),
            0,
        )
        self.assertEqual(
            len(
                list(
                    rule.additionalProperties(
                        validator,
                        False,
                        {**base_object, **{"c": "c"}},
                        schema,
                    )
                )
            ),
            1,
        )

        self.assertEqual(
            len(
                list(
                    rule.additionalProperties(
                        validator,
                        False,
                        {**base_object, **{"c": "c", "d": "d"}},
                        schema,
                    )
                )
            ),
            2,
        )

        self.assertEqual(
            len(
                list(
                    rule.additionalProperties(
                        validator,
                        True,
                        {**base_object, **{"c": "c"}},
                        schema,
                    )
                )
            ),
            0,
        )

        self.assertEqual(
            len(
                list(
                    rule.additionalProperties(
                        validator,
                        {
                            "type": "object",
                            "properties": {
                                "c": {
                                    "type": "string",
                                },
                            },
                        },
                        {**base_object, **{"c": {"c": "c"}}},
                        schema,
                    )
                )
            ),
            0,
        )

        self.assertEqual(
            len(
                list(
                    rule.additionalProperties(
                        validator,
                        False,
                        {**base_object, **{"c": "c"}},
                        {**schema, **{"patternProperties": "^c$"}},
                    )
                )
            ),
            0,
        )

        self.assertEqual(
            len(
                list(
                    rule.additionalProperties(
                        validator,
                        False,
                        {**base_object, **{"c": "c"}},
                        {
                            **schema,
                            **{
                                "patternProperties": {
                                    "^d$": {"type": "string"},
                                }
                            },
                        },
                    )
                )
            ),
            1,
        )
