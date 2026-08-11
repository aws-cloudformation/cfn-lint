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

    def test_invalid_logical_name_serverless_stays_e3001(self):
        """Invalid logical name (my-func) with Serverless Type stays E3001.

        Covers the len(err.path) < 2 guard - a top-level additionalProperties
        violation (path length 1) must stay E3001, not become W3001.
        """
        validator = CfnTemplateValidator({})

        errors = list(
            self.rule.validate(
                validator,
                "cfnResources",
                {
                    "my-func": {
                        "Type": "AWS::Serverless::Function",
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
        self.assertEqual(errors[0].rule.id, "E3001")
        self.assertEqual(errors[0].validator, "additionalProperties")
        self.assertEqual(len(errors[0].path), 1)
        self.assertIn("my-func", errors[0].message)

    def test_non_additional_properties_error_passes_through(self):
        """Non-additionalProperties error on Serverless resource passes through.

        Covers the err.validator != "additionalProperties" guard.
        """
        validator = CfnTemplateValidator({})

        errors = list(
            self.rule.validate(
                validator,
                "cfnResources",
                {
                    "Function": {
                        "Type": ["AWS::Serverless::Function"],
                        "Properties": {},
                    }
                },
                {},
            )
        )

        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].rule.id, "E3001")
        self.assertEqual(errors[0].validator, "type")
        self.assertIn("is not of type 'string'", errors[0].message)

    def test_multiple_unknown_attrs_multiple_w3001(self):
        """Multiple unknown resource-level attrs produce multiple W3001 findings."""
        validator = CfnTemplateValidator({})

        errors = list(
            self.rule.validate(
                validator,
                "cfnResources",
                {
                    "Function": {
                        "Type": "AWS::Serverless::Function",
                        "Description": "Wrong level",
                        "Handler": "Also wrong level",
                        "Runtime": "python3.12",
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

        self.assertEqual(len(errors), 3)
        for error in errors:
            self.assertEqual(error.rule.id, "W3001")
            self.assertIn(
                "Additional resource properties are ignored by the SAM transform",
                error.message,
            )

    def test_other_sam_types_w3001(self):
        """Other SAM types beyond Function with stray resource-level attr get W3001."""
        validator = CfnTemplateValidator({})

        # AWS::Serverless::Api
        errors = list(
            self.rule.validate(
                validator,
                "cfnResources",
                {
                    "Api": {
                        "Type": "AWS::Serverless::Api",
                        "Description": "Wrong level",
                        "Properties": {
                            "StageName": "prod",
                        },
                    }
                },
                {},
            )
        )

        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].rule.id, "W3001")

        # AWS::Serverless::StateMachine
        errors = list(
            self.rule.validate(
                validator,
                "cfnResources",
                {
                    "StateMachine": {
                        "Type": "AWS::Serverless::StateMachine",
                        "Description": "Wrong level",
                        "Properties": {
                            "Definition": {},
                        },
                    }
                },
                {},
            )
        )

        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].rule.id, "W3001")

        # AWS::Serverless::SimpleTable
        errors = list(
            self.rule.validate(
                validator,
                "cfnResources",
                {
                    "Table": {
                        "Type": "AWS::Serverless::SimpleTable",
                        "Description": "Wrong level",
                        "Properties": {},
                    }
                },
                {},
            )
        )

        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].rule.id, "W3001")

    def test_valid_sam_resource_no_w3001(self):
        """Valid SAM resource with only allowed attrs produces no W3001."""
        validator = CfnTemplateValidator({})

        errors = list(
            self.rule.validate(
                validator,
                "cfnResources",
                {
                    "Function": {
                        "Type": "AWS::Serverless::Function",
                        "Condition": "IsProduction",
                        "DependsOn": "AnotherResource",
                        "Metadata": {"key": "value"},
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

        w3001_errors = [e for e in errors if e.rule.id == "W3001"]
        self.assertEqual(len(w3001_errors), 0)

    def test_did_you_mean_message_variant_w3001(self):
        """Stray key close to a valid one gets rewritten W3001 with 'Did you mean'."""
        validator = CfnTemplateValidator({})

        errors = list(
            self.rule.validate(
                validator,
                "cfnResources",
                {
                    "Function": {
                        "Type": "AWS::Serverless::Function",
                        "Propertiez": {
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
        self.assertIn(
            "Additional resource properties are ignored by the SAM transform",
            errors[0].message,
        )
        self.assertIn("Did you mean", errors[0].message)
