"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import logging
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.resources.cloudformation.ServiceTimeout import ServiceTimeout


class TestServiceTimeout(BaseRuleTestCase):
    """Test CloudFormation Nested stack parameters"""

    def tearDown(self) -> None:
        super().tearDown()
        logger = logging.getLogger("cfnlint.decode.decode")
        logger.disabled = False

    def setUp(self):
        """Setup"""
        super(ServiceTimeout, self).setUp()
        self.collection.register(ServiceTimeout())
        logger = logging.getLogger("cfnlint.decode.decode")
        logger.disabled = True
        self.success_templates = [
            "test/fixtures/templates/good/resources/cloudformation/service_timeout.yaml"
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        err_count = 2
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources/cloudformation/service_timeout.yaml",
            err_count,
        )
