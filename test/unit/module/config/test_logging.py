"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import logging
from test.testlib.testcase import BaseTestCase

import cfnlint.config  # pylint: disable=E0401

LOGGER = logging.getLogger("cfnlint")


class TestLogging(BaseTestCase):
    """Test Logging Arguments"""

    def tearDown(self):
        """Setup"""
        for handler in LOGGER.handlers:
            LOGGER.removeHandler(handler)

    def test_logging_info(self):
        """Test success run"""

        cfnlint.config.configure_logging(False, True)
        self.assertEqual(logging.INFO, LOGGER.level)
        self.assertEqual(len(LOGGER.handlers), 1)

    def test_logging_debug(self):
        """Test debug level"""

        cfnlint.config.configure_logging(True, False)
        self.assertEqual(logging.DEBUG, LOGGER.level)
        self.assertEqual(len(LOGGER.handlers), 1)

    def test_no_logging(self):
        """Test no logging level"""

        cfnlint.config.configure_logging(False, False)
        self.assertEqual(logging.WARNING, LOGGER.level)
        self.assertEqual(len(LOGGER.handlers), 1)
