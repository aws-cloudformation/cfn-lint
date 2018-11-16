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
import cfnlint.helpers
import json
from cfnlint.rules.resources.properties.Properties import Properties  # pylint: disable=E0401
from ... import BaseRuleTestCase


class TestResourceProperties(BaseRuleTestCase):
    """Test Resource Properties"""
    def setUp(self):
        """Setup"""
        super(TestResourceProperties, self).setUp()
        self.collection.register(Properties())
        self.success_templates = [
            'fixtures/templates/good/resource_properties.yaml',
            'fixtures/templates/good/resources/properties/templated_code.yaml',
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        self.helper_file_negative('fixtures/templates/bad/generic.yaml', 9)

    def test_file_negative_2(self):
        """Failure test"""
        self.helper_file_negative('fixtures/templates/bad/object_should_be_list.yaml', 4)

    def test_file_negative_3(self):
        """Failure test"""
        self.helper_file_negative('fixtures/templates/bad/resource_properties.yaml', 4)


class TestSpecifiedCustomResourceProperties(TestResourceProperties):
    """Repeat Resource Properties tests with Custom Resource override spec provided"""
    def setUp(self):
        """Setup"""
        super(TestSpecifiedCustomResourceProperties, self).setUp()
        # Add a Spec override that specifies the Custom::SpecifiedCustomResource type
        with open('fixtures/templates/override_spec/custom.json') as fp:
            custom_spec = json.load(fp)
        cfnlint.helpers.set_specs(custom_spec)
        # Reset Spec override after test
        self.addCleanup(cfnlint.helpers.initialize_specs)

    # ... all TestResourceProperties test cases are re-run with override spec ...

    def test_file_negative_custom(self):
        """Additional failure test for specified Custom Resource validation"""
        self.helper_file_negative('fixtures/templates/bad/resources/properties/custom.yaml', 2)
