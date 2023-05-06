"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from typing import Generator
from unittest import TestCase

from jsonschema import Draft7Validator

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.BaseJsonSchemaValidator import BaseJsonSchemaValidator


class Rule(BaseJsonSchemaValidator):
    def validate_value(
        self, validator, s, instance, schema, **kwargs
    ) -> Generator[ValidationError, None, None]:
        if not instance:
            yield ValidationError("Failure")


class TestBaseJsonSchemaValidator(TestCase):
    """Test Base JSON Schema validation"""

    def test_base_functions(self):
        rule = Rule()
        validator = Draft7Validator(
            {
                "type": "string",
                "maxLength": 1,
            }
        )

        self.assertEqual(len(list(rule.validate_instance(validator, {}, True, {}))), 0)
        self.assertEqual(
            len(list(rule.validate_instance(validator, {}, {"Ref": "Foo"}, {}))), 0
        )
        self.assertEqual(
            len(
                list(
                    rule.validate_instance(validator, {}, {"Fn::GetAtt": "Foo.Bar"}, {})
                )
            ),
            0,
        )
        self.assertEqual(
            len(
                list(
                    rule.validate_instance(
                        validator, {}, {"Fn::FindInMap": ["Foo", "Bar", "Key"]}, {}
                    )
                )
            ),
            0,
        )
        self.assertEqual(
            len(
                list(
                    rule.validate_instance(
                        validator, {}, {"Fn::GetAZs": "us-east-1"}, {}
                    )
                )
            ),
            0,
        )
        self.assertEqual(
            len(
                list(
                    rule.validate_instance(
                        validator, {}, {"Fn::ImportValue": "Foo"}, {}
                    )
                )
            ),
            0,
        )
        self.assertEqual(
            len(
                list(
                    rule.validate_instance(
                        validator, {}, {"Fn::Join": ["Foo", "Bar"]}, {}
                    )
                )
            ),
            0,
        )
        self.assertEqual(
            len(
                list(rule.validate_instance(validator, {}, {"Fn::Split": "FooBar"}, {}))
            ),
            0,
        )
        self.assertEqual(
            len(
                list(
                    rule.validate_instance(
                        validator, {}, {"Fn::Select": ["Foo", "Bar"]}, {}
                    )
                )
            ),
            0,
        )
        self.assertEqual(
            len(
                list(
                    rule.validate_instance(
                        validator, {}, {"Fn::Sub": "${Foo}-${Bar}"}, {}
                    )
                )
            ),
            0,
        )
        self.assertEqual(
            len(
                list(
                    rule.validate_instance(
                        validator, {}, {"Fn::If": ["Foo", False, False]}, {}
                    )
                )
            ),
            2,
        )
        self.assertEqual(
            len(
                list(
                    rule.validate_instance(
                        validator,
                        {},
                        {
                            "Fn::If": [
                                "Foo",
                                False,
                            ]
                        },
                        {},
                    )
                )
            ),
            0,
        )
        self.assertEqual(
            len(
                list(
                    rule.validate_instance(
                        validator,
                        {},
                        {"Fn::Cidr": ["ipBlock", "count", "cidrBits"]},
                        {},
                    )
                )
            ),
            0,
        )
        self.assertEqual(
            len(
                list(
                    rule.validate_instance(
                        validator, {}, {"Fn::Length": ["foo", "bar"]}, {}
                    )
                )
            ),
            0,
        )
        self.assertEqual(
            len(
                list(
                    rule.validate_instance(
                        validator, {}, {"Fn::ToJsonString": {"foo": "bar"}}, {}
                    )
                )
            ),
            0,
        )
