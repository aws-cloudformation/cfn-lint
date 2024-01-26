"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.resources.PreviousGenerationInstanceType import (
    PreviousGenerationInstanceType,  # pylint: disable=E0401
)


class TestPreviousGenerationInstanceType(BaseRuleTestCase):
    def setUp(self):
        super(TestPreviousGenerationInstanceType, self).setUp()
        self.collection.register(PreviousGenerationInstanceType())

    def test_file_positive(self):
        self.helper_file_positive()

    def test_file_negative(self):
        self.helper_file_negative(
            "test/fixtures/templates/bad/previous_generation_instances.yaml", 4
        )
