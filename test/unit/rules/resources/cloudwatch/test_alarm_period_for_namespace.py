"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.resources.cloudwatch.AlarmPeriodInSeconds import (
    AlarmPeriodInSecondsAWSNamespace,
    AlarmPeriodInSecondsSmallInterval,
)


class TestMatchProjectValidateRule(BaseRuleTestCase):
    """Test template mapping configurations"""

    def setUp(self):
        """Setup"""
        super(TestMatchProjectValidateRule, self).setUp()
        for rule in [
            AlarmPeriodInSecondsAWSNamespace(),
            AlarmPeriodInSecondsSmallInterval(),
        ]:
            self.collection.register(rule)

    success_templates = [
        "test/fixtures/templates/good/resources/cloudwatch/alarm_period_for_namespace.yaml"
    ]

    def test_file_positive(self):
        self.helper_file_positive()

    def test_file_negative(self):
        errs = self.run_file_negative(
            "test/fixtures/templates/bad/resources/cloudwatch/alarm_period_for_namespace.yaml"
        )
        self.assertEqual(
            errs,
            [
                {
                    "Filename": "test/fixtures/templates/bad/resources/cloudwatch/alarm_period_for_namespace.yaml",
                    "Level": "Error",
                    "Location": {
                        "End": {"ColumnNumber": 13, "LineNumber": 8},
                        "Path": [
                            "Resources",
                            "AWSNamespaceNumeric30",
                            "Properties",
                            "Period",
                        ],
                        "Start": {"ColumnNumber": 7, "LineNumber": 8},
                    },
                    "Message": "Period in AWS Namespace should be 60 or multiple of 60",
                    "Rule": {
                        "Description": "AWS::CloudWatch::Alarm: Period in AWS Namespace should be at least 60",
                        "Id": "E2555",
                        "ShortDescription": "E2555",
                        "Source": "",
                    },
                },
                {
                    "Filename": "test/fixtures/templates/bad/resources/cloudwatch/alarm_period_for_namespace.yaml",
                    "Level": "Error",
                    "Location": {
                        "End": {"ColumnNumber": 13, "LineNumber": 28},
                        "Path": [
                            "Resources",
                            "AWSNamespaceString30",
                            "Properties",
                            "Period",
                        ],
                        "Start": {"ColumnNumber": 7, "LineNumber": 28},
                    },
                    "Message": "Period in AWS Namespace should be 60 or multiple of 60",
                    "Rule": {
                        "Description": "AWS::CloudWatch::Alarm: Period in AWS Namespace should be at least 60",
                        "Id": "E2555",
                        "ShortDescription": "E2555",
                        "Source": "",
                    },
                },
                {
                    "Filename": "test/fixtures/templates/bad/resources/cloudwatch/alarm_period_for_namespace.yaml",
                    "Level": "Error",
                    "Location": {
                        "End": {"ColumnNumber": 13, "LineNumber": 38},
                        "Path": [
                            "Resources",
                            "MyNamespaceNumeric44",
                            "Properties",
                            "Period",
                        ],
                        "Start": {"ColumnNumber": 7, "LineNumber": 38},
                    },
                    "Message": "Period <= 60 can only be [10, 30, 60]",
                    "Rule": {
                        "Description": "AWS::CloudWatch::Alarm: Period <= 60 can only be [10, 30, 60]",
                        "Id": "E2556",
                        "ShortDescription": "E2556",
                        "Source": "",
                    },
                },
            ],
        )
