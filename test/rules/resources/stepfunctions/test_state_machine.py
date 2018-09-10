"""
  Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.

  Permission is hereby granted, free of charge, to any person obtaining a copy of this
  software and associated documentation files (the "Software"), to deal in the Software
  without restriction, including without limitation the rights to use, copy, modify,
  merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
  permit persons to whom the Software is furnished to do so.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
  INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
  PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
  HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
  OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
  SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
from cfnlint.rules.resources.stepfunctions.StateMachine import StateMachine  # pylint: disable=E0401
from ... import BaseRuleTestCase


class TestStateMachine(BaseRuleTestCase):
    """Test StateMachine for Step Functions"""
    def setUp(self):
        """Setup"""
        super(TestStateMachine, self).setUp()
        self.collection.register(StateMachine())
        self.success_templates = [
            'fixtures/templates/good/resources/stepfunctions/state_machine.yaml'
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative_alias(self):
        """Test failure"""
        self.helper_file_negative('fixtures/templates/bad/resources/stepfunctions/state_machine.yaml', 5)
