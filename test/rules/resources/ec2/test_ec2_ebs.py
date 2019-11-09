"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules.resources.ectwo.Ebs import Ebs  # pylint: disable=E0401
from ... import BaseRuleTestCase


class TestPropertyEc2Ebs(BaseRuleTestCase):
    """Test Ebs Property Configuration"""
    def setUp(self):
        """Setup"""
        super(TestPropertyEc2Ebs, self).setUp()
        self.collection.register(Ebs())

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative('test/fixtures/templates/bad/properties_ebs.yaml', 3)
