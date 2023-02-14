"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from jsonschema import Draft7Validator

from cfnlint.rules.resources.properties.ListDuplicates import (
    ListDuplicates,  # pylint: disable=E0401
)
from cfnlint.rules.resources.properties.ListDuplicatesAllowed import (
    ListDuplicatesAllowed,  # pylint: disable=E0401
)


class TestListDuplicates(BaseRuleTestCase):
    """Test List duplicates"""

    def test_duplicate(self):
        rule = ListDuplicates()
        validator = Draft7Validator(
            {"type": "array", "items": [{"type": "string"}], "uniqueItems": True}
        )
        self.assertEqual(
            len(list(rule.uniqueItems(validator, True, ["a", "b"], {}))), 0
        )
        self.assertEqual(
            len(list(rule.uniqueItems(validator, True, ["a", "a"], {}))), 1
        )
        self.assertEqual(len(list(rule.uniqueItems(validator, True, [0, 1], {}))), 0)
        self.assertEqual(len(list(rule.uniqueItems(validator, True, [0, 0], {}))), 1)
        self.assertEqual(
            len(
                list(
                    rule.uniqueItems(
                        validator,
                        True,
                        [
                            {"Key": "key", "Value": "value"},
                            {"Key": "key", "Value": "value"},
                        ],
                        {},
                    )
                )
            ),
            1,
        )
        self.assertEqual(
            len(
                list(
                    rule.uniqueItems(
                        validator,
                        True,
                        [
                            {"Key": "key", "Value": "value"},
                            {"Key": "key", "Value": "another"},
                        ],
                        {},
                    )
                )
            ),
            0,
        )
        self.assertEqual(
            len(list(rule.uniqueItems(validator, True, [["a"], ["a"]], {}))), 1
        )
        self.assertEqual(
            len(list(rule.uniqueItems(validator, True, [["a"], ["a", "b"]], {}))), 0
        )
        self.assertEqual(
            len(list(rule.uniqueItems(validator, True, [["a"], ["b"]], {}))), 0
        )

    def test_duplicate_info(self):
        rule = ListDuplicates()
        rule.child_rules["I3037"] = ListDuplicatesAllowed()
        validator = Draft7Validator(
            {"type": "array", "items": [{"type": "string"}], "uniqueItems": True}
        )
        err = list(rule.uniqueItems(validator, False, ["a", "a"], {}))
        self.assertEqual(len(err), 1)
        self.assertEqual(err[0].rule.id, "I3037")

        err = list(rule.uniqueItems(validator, False, ["a", "b"], {}))
        self.assertEqual(len(err), 0)
