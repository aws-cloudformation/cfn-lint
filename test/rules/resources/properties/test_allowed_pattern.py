"""
  Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.

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
import json
import pkg_resources
import re
from cfnlint.rules.resources.properties.AllowedPattern import AllowedPattern  # pylint: disable=E0401
from ... import BaseRuleTestCase


class TestAllowedPattern(BaseRuleTestCase):
    """Test Allowed Value Property Configuration"""
    def setUp(self):
        """Setup"""
        super(TestAllowedPattern, self).setUp()
        self.collection.register(AllowedPattern())

        # Load the specfile to validate all the regexes specified
        filename = '../../../../src/cfnlint/data/CloudSpecs/us-east-1.json'
        filename = pkg_resources.resource_filename(
            __name__,
            filename
        )

        with open(filename) as fp:
            self.spec = json.load(fp)

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative_sg_ingress(self):
        """Test failure"""
        self.helper_file_negative('test/fixtures/templates/bad/properties_sg_ingress.yaml', 2)

    def test_valid_regex(self):
        """Test Resource Type Value Regex"""
        for r_name, r_values in self.spec.get('ValueTypes').items():
            if r_values.get('AllowedPatternRegex'):
                p_regex = r_values.get('AllowedPatternRegex')
                try:
                    re.compile(p_regex)
                except re.error:
                    self.fail("Invalid regex value %s specified for ValueType %s" % (p_regex, r_name))
