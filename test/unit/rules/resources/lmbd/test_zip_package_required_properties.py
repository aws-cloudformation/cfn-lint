"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.resources.lmbd.ZipPackageRequiredProperties import (
    ZipPackageRequiredProperties,
)


class TestZipPackageRequiredProperties(BaseRuleTestCase):
    """Test required properties"""

    def setUp(self):
        super(TestZipPackageRequiredProperties, self).setUp()
        self.collection.register(ZipPackageRequiredProperties())
        self.success_templates = [
            "test/fixtures/templates/good/resources/lambda/required_properties.yaml"
        ]

    def test_file_positive(self):
        self.helper_file_positive()

    def test_file_negative(self):
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources/lambda/required_properties.yaml",
            err_count=3,
        )
