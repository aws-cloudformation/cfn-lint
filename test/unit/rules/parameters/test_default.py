"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.parameters.Default import Default  # pylint: disable=E0401
from cfnlint.template import Template


class TestDefault(BaseRuleTestCase):
    """Test template parameter configurations"""

    def setUp(self):
        """Setup"""
        super(TestDefault, self).setUp()
        self.collection.register(Default())

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_parameters_success(self):
        self.helper_file_positive_template(
            "test/fixtures/templates/good/parameters/default.yaml"
        )

    def test_parameters_success_json(self):
        self.helper_file_positive_template(
            "test/fixtures/templates/good/parameters/default.json"
        )

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/parameters/default.yaml", 13
        )

    def test_malformed_constraints_do_not_crash(self):
        """Malformed constraint types are reported by E2001, not by a crash"""
        rule = Default()
        for constraint in (
            {"AllowedValues": True},
            {"AllowedValues": 5},
            {"AllowedValues": "abc"},
            {"AllowedPattern": 5},
            {"AllowedPattern": ["a"]},
        ):
            with self.subTest(constraint=constraint):
                template = Template(
                    "",
                    {
                        "Parameters": {
                            "P": {"Type": "String", "Default": "a", **constraint}
                        },
                        "Resources": {},
                    },
                )
                self.assertEqual(rule.match(template), [])
