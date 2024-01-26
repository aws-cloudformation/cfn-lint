"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.functions.ForEach import ForEach


class TestForEach(BaseRuleTestCase):
    def setUp(self):
        super(TestForEach, self).setUp()
        self.collection.register(ForEach())
        self.success_templates = [
            "test/fixtures/templates/good/functions/foreach.yaml",
        ]

    def test_file_positive(self):
        self.helper_file_positive()

    def test_file_negative_missing_transform(self):
        self.helper_file_negative(
            "test/fixtures/templates/bad/functions/foreach_no_transform.yaml", 3
        )
