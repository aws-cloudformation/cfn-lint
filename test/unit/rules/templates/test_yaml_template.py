"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.unit.rules import BaseRuleTestCase

from cfnlint.rules import Rules
from cfnlint.rules.jsonschema.JsonSchema import JsonSchema
from cfnlint.runner import Runner


class TestBaseTemplate(BaseRuleTestCase):
    """Test base template"""

    def setUp(self):
        """Setup"""
        self.collection = Rules()
        self.collection.register(JsonSchema())

    def test_file_negative(self):
        """Failure test"""
        failure = "test/fixtures/templates/bad/template.yaml"
        try:
            Runner(self.collection, failure, True)
            self.assertEqual(1, 0)
        except Exception:
            pass
