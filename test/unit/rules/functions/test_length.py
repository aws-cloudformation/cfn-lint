"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase
from cfnlint.rules.functions.Length import Length


class TestRulesLength(BaseRuleTestCase):
    """Test Rules Get Att """

    def setUp(self):
        super(TestRulesLength, self).setUp()
        self.collection.register(Length())
        self.success_templates = [
            'test/fixtures/templates/good/functions/length.yaml',
        ]

    def test_file_positive(self):
        self.helper_file_positive()

    def test_file_negative(self):
        self.helper_file_negative('test/fixtures/templates/bad/functions/lengthWithoutTransform.yaml', 1)
