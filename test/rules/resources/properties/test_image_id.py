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
from cfnlint import RulesCollection  # pylint: disable=E0401
from cfnlint.rules.resources.properties.ImageId import ImageId  # pylint: disable=E0401
from ... import BaseRuleTestCase


class TestPropertyVpcId(BaseRuleTestCase):
    """Test Password Property Configuration"""
    def setUp(self):
        """Setup"""
        super(TestPropertyVpcId, self).setUp()
        self.collection.register(ImageId())

    success_templates = [
        'fixtures/templates/good/generic.yaml',
    ]

    def test_file_positive(self):
        """Success test"""
        self.helper_file_positive()

    def test_file_negative_nist_app(self):
        """Failure test"""
        self.helper_file_negative('fixtures/templates/quickstart/nist_application.yaml', 2)

    def test_file_negative_nist_mgmt(self):
        """Failure test"""
        self.helper_file_negative('fixtures/templates/quickstart/nist_vpc_management.yaml', 1)

    def test_file_negative(self):
        """Failure test"""
        self.helper_file_negative('fixtures/templates/bad/properties_imageid.yaml', 1)
