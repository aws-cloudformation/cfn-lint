"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.resources.lmbd.RuntimeCanUseZipFile import RuntimeCanUseZipFile


class TestMatchProjectValidateRule(BaseRuleTestCase):
    """Test template mapping configurations"""

    def setUp(self):
        """Setup"""
        super(TestMatchProjectValidateRule, self).setUp()
        for rule in [RuntimeCanUseZipFile()]:
            self.collection.register(rule)

    success_templates = [
        "test/fixtures/templates/good/resources/lambda/runtime_can_use_code_zip_file.yaml"
    ]

    def test_file_positive(self):
        self.helper_file_positive()

    def test_file_negative(self):
        errs = self.run_file_negative(
            "test/fixtures/templates/bad/resources/lambda/runtime_can_use_code_zip_file.yaml"
        )
        self.assertEqual(
            errs,
            [
                {
                    "Filename": "test/fixtures/templates/bad/resources/lambda/runtime_can_use_code_zip_file.yaml",
                    "Level": "Error",
                    "Location": {
                        "End": {"ColumnNumber": 16, "LineNumber": 5},
                        "Path": [
                            "Resources",
                            "GoZipFile",
                            "Properties",
                            "Code",
                            "ZipFile",
                            "Fn::Sub",
                        ],
                        "Start": {"ColumnNumber": 9, "LineNumber": 5},
                    },
                    "Message": "Zipfile can only be use for Nodejs or Python Runtime",
                    "Rule": {
                        "Description": "AWS::Lambda::Function: Zipfile can only be use for Runtime Nodejs*",
                        "Id": "E2553",
                        "ShortDescription": "E2553",
                        "Source": "",
                    },
                }
            ],
        )
