"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.resources.certificatemanager.DomainValidationOptions import (
    DomainValidationOptions,
)


class TestDomainValidationOptions(BaseRuleTestCase):
    """Test ValidationDomainOptions Configuration"""

    def setUp(self):
        """Setup"""
        super(TestDomainValidationOptions, self).setUp()
        self.collection.register(DomainValidationOptions())

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive_template(
            "test/fixtures/templates/good/resources/certificatemanager/domain_validation_options.yaml"
        )

    def test_file_negative_invalid_validationdomain(self):
        """Test failure"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources/certificatemanager/domain_validation_options.yaml",
            2,
        )
