"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import json
from test.unit.rules import BaseRuleTestCase

import cfnlint.helpers
from cfnlint.rules.resources.properties.Required import (
    Required,  # pylint: disable=E0401
)


class TestResourceConfiguration(BaseRuleTestCase):
    """Test Resource Properties"""

    def setUp(self):
        """Setup"""
        super(TestResourceConfiguration, self).setUp()
        self.collection.register(Required())
        self.success_templates = [
            "test/fixtures/templates/good/resources/properties/required.yaml",
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/properties_required.yaml", 11
        )

    def test_file_negative_generic(self):
        """Generic Test failure"""
        self.helper_file_negative("test/fixtures/templates/bad/generic.yaml", 8)


class TestSpecifiedCustomResourceRequiredProperties(TestResourceConfiguration):
    """Test Custom Resource Required Properties when override spec is provided"""

    def setUp(self):
        """Setup"""
        super(TestSpecifiedCustomResourceRequiredProperties, self).setUp()
        # Add a Spec override that specifies the Custom::SpecifiedCustomResource type
        with open("test/fixtures/templates/override_spec/custom.json") as fp:
            custom_spec = json.load(fp)
        cfnlint.helpers.set_specs(custom_spec)
        # Reset Spec override after test
        self.addCleanup(cfnlint.helpers.initialize_specs)

    # ... all TestResourceConfiguration test cases are re-run with override spec ...

    def test_file_negative(self):
        """Test failure"""
        # Additional Custom::SpecifiedCustomResource failure detected with custom spec
        self.helper_file_negative(
            "test/fixtures/templates/bad/properties_required.yaml", 12
        )
