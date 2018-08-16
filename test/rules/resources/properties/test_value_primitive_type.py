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
from cfnlint.rules.resources.properties.ValuePrimitiveType import ValuePrimitiveType  # pylint: disable=E0401
from ... import BaseRuleTestCase


class TestResourceValuePrimitiveType(BaseRuleTestCase):
    """Test Primitive Value Types"""
    def setUp(self):
        """Setup"""
        super(TestResourceValuePrimitiveType, self).setUp()
        self.collection.register(ValuePrimitiveType())

    success_templates = [
        'fixtures/templates/good/generic.yaml',
        'fixtures/templates/good/resource_properties.yaml'
    ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative_nist_high_master(self):
        """Generic Test failure"""
        self.helper_file_negative('fixtures/templates/quickstart/nist_high_master.yaml', 6)

    def test_file_negative_nist_high_app(self):
        """Generic Test failure"""
        self.helper_file_negative('fixtures/templates/quickstart/nist_application.yaml', 53)

    def test_file_negative_nist_config_rules(self):
        """Generic Test failure"""
        self.helper_file_negative('fixtures/templates/quickstart/nist_config_rules.yaml', 1)

    def test_file_negative_generic(self):
        """Generic Test failure"""
        self.helper_file_negative('fixtures/templates/bad/generic.yaml', 3)
