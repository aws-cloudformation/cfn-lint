"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque
from test.unit.rules import BaseRuleTestCase

from cfnlint.context import Context, Path
from cfnlint.jsonschema import CfnTemplateValidator
from cfnlint.rules.parameters.Enum import Enum


class TestAllowedValue(BaseRuleTestCase):
    """Test Allowed Value Parameter Configuration"""

    def setUp(self):
        """Setup"""
        self.rule = Enum()

    def test_validate(self):
        validator = CfnTemplateValidator(
            schema={"type": "string"},
            context=Context(
                "us-east-1",
                {},
                path=Path(
                    path=deque(["Property", "Ref"]),
                    value_path=deque(["Parameters", "MyParameter", "Default"]),
                ),
            ),
        )

        errs = list(self.rule.enum(validator, "1", ["A", "B"], {}))
        self.assertEqual(len(errs), 1)
        self.assertEqual(len(errs), 1)
        for err in errs:
            self.assertEqual(err.message, "['A', 'B'] is not one of '1'")
            self.assertEqual(err.rule, self.rule)
            self.assertEqual(
                err.path_override, deque(["Parameters", "MyParameter", "Default"])
            )
