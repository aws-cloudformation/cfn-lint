"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.resources.UniqueNames import UniqueNames  # pylint: disable=E0401


class TestUniqueNames(BaseRuleTestCase):
    def setUp(self):
        super(TestUniqueNames, self).setUp()
        self.collection.register(UniqueNames())

    def test_file_positive(self):
        self.helper_file_positive()

    def test_file_negative(self):
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources/uniqueNames.yaml", 1
        )
