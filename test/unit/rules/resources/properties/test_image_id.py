"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.resources.properties.ImageId import ImageId  # pylint: disable=E0401


class TestPropertyVpcId(BaseRuleTestCase):
    """Test Password Property Configuration"""

    def setUp(self):
        """Setup"""
        super(TestPropertyVpcId, self).setUp()
        self.collection.register(ImageId())

    success_templates = [
        "test/fixtures/templates/good/generic.yaml",
        "test/fixtures/templates/good/properties_imageid.yaml",
    ]

    def test_file_positive(self):
        """Success test"""
        self.helper_file_positive()

    def test_file_negative_nist_app(self):
        """Failure test"""
        self.helper_file_negative(
            "test/fixtures/templates/quickstart/nist_application.yaml", 2
        )

    def test_file_negative_nist_mgmt(self):
        """Failure test"""
        self.helper_file_negative(
            "test/fixtures/templates/quickstart/nist_vpc_management.yaml", 1
        )

    def test_file_negative(self):
        """Failure test"""
        self.helper_file_negative(
            "test/fixtures/templates/bad/properties_imageid.yaml", 1
        )
