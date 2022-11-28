"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.functions.Length import Length


class TestRulesLength(BaseRuleTestCase):
    def setUp(self):
        super(TestRulesLength, self).setUp()
        self.collection.register(Length())
        self.success_templates = [
            "test/fixtures/templates/good/functions/length.yaml",
        ]

    def test_file_positive(self):
        self.helper_file_positive()

    def test_file_negative_missing_transform(self):
        self.helper_file_negative(
            "test/fixtures/templates/bad/functions/lengthWithoutTransform.yaml", 1
        )

    def test_file_negative_wrong_types(self):
        self.helper_file_negative(
            "test/fixtures/templates/bad/functions/lengthWrongTypes.yaml", 7
        )
