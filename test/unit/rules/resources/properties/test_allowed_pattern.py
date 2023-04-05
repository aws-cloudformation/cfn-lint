"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

import regex as re

from cfnlint.data import CloudSpecs
from cfnlint.helpers import RESOURCE_SPECS, load_resource
from cfnlint.rules.resources.properties.AllowedPattern import (
    AllowedPattern,  # pylint: disable=E0401
)


class TestAllowedPattern(BaseRuleTestCase):
    """Test Allowed Value Property Configuration"""

    def setUp(self):
        """Setup"""
        super(TestAllowedPattern, self).setUp()
        self.collection.register(AllowedPattern())
        self.success_templates = [
            "test/fixtures/templates/good/resources/properties/allowed_pattern.yaml"
        ]

        self.spec = RESOURCE_SPECS["us-east-1"]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_template_config(self):
        """Test strict false"""
        self.helper_file_rule_config(
            "test/fixtures/templates/bad/properties_sg_ingress.yaml",
            {"exceptions": ["Special charaters*"]},
            1,
        )

    def test_file_negative_sg_ingress(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/properties_sg_ingress.yaml", 2
        )

    def test_valid_regex(self):
        """Test Resource Type Value Regex"""
        for r_name, r_values in self.spec.get("ValueTypes").items():
            if r_values.get("AllowedPatternRegex"):
                p_regex = r_values.get("AllowedPatternRegex")
                try:
                    re.compile(p_regex)
                except re.error:
                    self.fail(
                        "Invalid regex value %s specified for ValueType %s"
                        % (p_regex, r_name)
                    )
