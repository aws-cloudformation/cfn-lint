"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint import Runner  # pylint: disable=E0401
from cfnlint.rules import RulesCollection
from cfnlint.rules.templates.Base import Base  # pylint: disable=E0401
from .. import BaseRuleTestCase


class TestBaseTemplate(BaseRuleTestCase):
    """Test base template"""

    def setUp(self):
        """Setup"""
        self.collection = RulesCollection()
        self.collection.register(Base())

    def test_file_negative(self):
        """Failure test"""
        failure = 'test/fixtures/templates/bad/template.yaml'
        try:
            Runner(self.collection, failure, True)
            self.assertEqual(1, 0)
        except Exception:
            pass
