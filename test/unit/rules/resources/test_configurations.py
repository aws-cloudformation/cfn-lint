"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque
from test.unit.rules import BaseRuleTestCase

from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules.resources.Configuration import Configuration


class TestResourceConfiguration(BaseRuleTestCase):
    """Test AWS Types"""

    def setUp(self):
        """Setup"""
        super(TestResourceConfiguration, self).setUp()
        self.rule = Configuration()

    def test_configurations(self):
        validator = CfnTemplateValidator({})
        errors = list(
            self.rule.validate(validator, "cfnResources", {"foo": {"Type": "bar"}}, {})
        )
        self.assertListEqual(
            errors,
            [],
            errors,
        )

        errors = list(self.rule.validate(validator, "cfnResources", {"foo": []}, {}))

        self.assertListEqual(
            errors,
            [
                ValidationError(
                    "[] is not of type 'object'",
                    rule=Configuration(),
                    path=deque(["foo"]),
                    schema_path=deque(["patternProperties", "^[a-zA-Z0-9]+$", "type"]),
                    validator="type",
                    validator_value="object",
                    instance=[],
                ),
            ],
            errors,
        )

    def test_serverless_additional_properties_are_warnings(self):
        validator = CfnTemplateValidator({})

        errors = list(
            self.rule.validate(
                validator,
                "cfnResources",
                {
                    "Function": {
                        "Type": "AWS::Serverless::Function",
                        "Description": "Wrong level",
                        "Properties": {
                            "CodeUri": "src/",
                            "Handler": "app.handler",
                            "Runtime": "python3.12",
                        },
                    }
                },
                {},
            )
        )

        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].rule.id, "W3001")
        self.assertEqual(
            errors[0].message,
            "Additional resource properties are ignored by the SAM transform "
            "('Description' was unexpected)",
        )

    def test_standard_resource_additional_properties_are_errors(self):
        validator = CfnTemplateValidator({})

        errors = list(
            self.rule.validate(
                validator,
                "cfnResources",
                {
                    "Bucket": {
                        "Type": "AWS::S3::Bucket",
                        "Description": "Wrong level",
                        "Properties": {},
                    }
                },
                {},
            )
        )

        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].rule.id, "E3001")

        errors = list(
            self.rule.validate(validator, "cfnResources", {"foo": {"Type": []}}, {})
        )

        self.assertListEqual(
            errors,
            [
                ValidationError(
                    "[] is not of type 'string'",
                    rule=Configuration(),
                    path=deque(["foo", "Type"]),
                    schema_path=deque(
                        [
                            "patternProperties",
                            "^[a-zA-Z0-9]+$",
                            "properties",
                            "Type",
                            "type",
                        ]
                    ),
                    validator="type",
                    validator_value="string",
                    instance=[],
                ),
            ],
            errors,
        )
