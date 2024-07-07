"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.unit.rules import BaseRuleTestCase

from cfnlint import ConfigMixIn
from cfnlint.rules.jsonschema.JsonSchema import JsonSchema


class TestBaseTemplate(BaseRuleTestCase):
    """Test base template"""

    def setUp(self):
        """Setup"""
        super(TestBaseTemplate, self).setUp()
        self.collection.register(JsonSchema())

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_positive_configured(self):
        self.helper_file_positive_template(
            "test/fixtures/templates/bad/generic.yaml",
            ConfigMixIn(
                [],
                configure_rules={
                    "E1001": {
                        "sections": "Errors",
                    }
                },
            ),
        )

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative("test/fixtures/templates/bad/generic.yaml", 1)

    def test_file_base(self):
        """Test failure"""
        self.helper_file_negative("test/fixtures/templates/bad/templates/base.yaml", 1)

    def test_file_base_date(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/templates/base_date.yaml", 1
        )

    def test_file_base_null(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/templates/base_null.yaml", 2
        )
