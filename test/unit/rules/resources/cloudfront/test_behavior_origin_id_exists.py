"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.resources.cloudfront.BehaviorOriginIdExists import (
    BehaviorOriginIdExists,
)


class TestMatchProjectValidateRule(BaseRuleTestCase):
    """Test template mapping configurations"""

    def setUp(self):
        """Setup"""
        super(TestMatchProjectValidateRule, self).setUp()
        for rule in [BehaviorOriginIdExists()]:
            self.collection.register(rule)

    success_templates = [
        "test/fixtures/templates/good/resources/cloudfront/behavior_origin_id_exists.yaml"
    ]

    def test_file_positive(self):
        self.helper_file_positive()

    def test_file_negative(self):
        errs = self.run_file_negative(
            "test/fixtures/templates/bad/resources/cloudfront/behavior_origin_id_exists.yaml"
        )
        self.assertEqual(
            errs,
            [
                {
                    "Filename": "test/fixtures/templates/bad/resources/cloudfront/behavior_origin_id_exists.yaml",
                    "Level": "Error",
                    "Location": {
                        "End": {"ColumnNumber": 27, "LineNumber": 24},
                        "Path": [
                            "Resources",
                            "MessedUpIds",
                            "Properties",
                            "DistributionConfig",
                            "CacheBehaviors",
                            1,
                            "TargetOriginId",
                        ],
                        "Start": {"ColumnNumber": 13, "LineNumber": 24},
                    },
                    "Message": "TargetOriginId should match one of the Origins.Id",
                    "Rule": {
                        "Description": "AWS::Cloudfront::Distribution: TargetOriginId should match one of the Origins.Id",
                        "Id": "E2554",
                        "ShortDescription": "E2554",
                        "Source": "",
                    },
                },
                {
                    "Filename": "test/fixtures/templates/bad/resources/cloudfront/behavior_origin_id_exists.yaml",
                    "Level": "Error",
                    "Location": {
                        "End": {"ColumnNumber": 27, "LineNumber": 34},
                        "Path": [
                            "Resources",
                            "MessedUpIds",
                            "Properties",
                            "DistributionConfig",
                            "CacheBehaviors",
                            2,
                            "TargetOriginId",
                        ],
                        "Start": {"ColumnNumber": 13, "LineNumber": 34},
                    },
                    "Message": "TargetOriginId should match one of the Origins.Id",
                    "Rule": {
                        "Description": "AWS::Cloudfront::Distribution: TargetOriginId should match one of the Origins.Id",
                        "Id": "E2554",
                        "ShortDescription": "E2554",
                        "Source": "",
                    },
                },
                {
                    "Filename": "test/fixtures/templates/bad/resources/cloudfront/behavior_origin_id_exists.yaml",
                    "Level": "Error",
                    "Location": {
                        "End": {"ColumnNumber": 25, "LineNumber": 44},
                        "Path": [
                            "Resources",
                            "MessedUpIds",
                            "Properties",
                            "DistributionConfig",
                            "DefaultCacheBehavior",
                            "TargetOriginId",
                        ],
                        "Start": {"ColumnNumber": 11, "LineNumber": 44},
                    },
                    "Message": "TargetOriginId should match one of the Origins.Id",
                    "Rule": {
                        "Description": "AWS::Cloudfront::Distribution: TargetOriginId should match one of the Origins.Id",
                        "Id": "E2554",
                        "ShortDescription": "E2554",
                        "Source": "",
                    },
                },
            ],
        )
