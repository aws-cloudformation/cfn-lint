"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import re
import json
from test.unit.rules import BaseRuleTestCase
from cfnlint.rules.resources.properties.AllowedPattern import AllowedPattern  # pylint: disable=E0401
from cfnlint.helpers import load_resource
from cfnlint.data import CloudSpecs


class TestAllowedPattern(BaseRuleTestCase):
    """Test Allowed Value Property Configuration"""

    def setUp(self):
        """Setup"""
        super(TestAllowedPattern, self).setUp()
        self.collection.register(AllowedPattern())
        self.success_templates = [
            'test/fixtures/templates/good/resources/properties/allowed_pattern.yaml'
        ]

        self.spec = load_resource(CloudSpecs, 'us-east-1.json')

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative_sg_ingress(self):
        """Test failure"""
        self.helper_file_negative('test/fixtures/templates/bad/properties_sg_ingress.yaml', 2)

    def test_valid_regex(self):
        """Test Resource Type Value Regex"""
        for r_name, r_values in self.spec.get('ValueTypes').items():
            if r_values.get('AllowedPatternRegex'):
                p_regex = r_values.get('AllowedPatternRegex')
                try:
                    re.compile(p_regex)
                except re.error:
                    self.fail("Invalid regex value %s specified for ValueType %s" %
                              (p_regex, r_name))
