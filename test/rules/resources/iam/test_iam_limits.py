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
from cfnlint.rules.resources.iam.Limits import Limits  # pylint: disable=E0401
from ... import BaseRuleTestCase


class TestPropertyIamLimits(BaseRuleTestCase):
    """Test IAM Limits"""
    def setUp(self):
        """Setup"""
        super(TestPropertyIamLimits, self).setUp()
        self.collection.register(Limits())

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_managedpolicyarns(self):
        """Test failure"""
        self.helper_file_negative('test/fixtures/templates/bad/resources_iam_managedpolicyarns.yaml', 3)

    def test_user_groups(self):
        """Test failure"""
        self.helper_file_negative('test/fixtures/templates/bad/resources_iam_user_groups.yaml', 1)

    def test_instance_profile_roles(self):
        """Test failure"""
        self.helper_file_negative('test/fixtures/templates/bad/resources_iam_instanceprofile_roles.yaml', 1)

    def test_role_assume_role_policy_document(self):
        """Test failure"""
        self.helper_file_negative('test/fixtures/templates/bad/resources_iam_role_assume_role_policy_document.yaml', 1)
