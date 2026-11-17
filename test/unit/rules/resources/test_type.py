"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque
from test.unit.rules import BaseRuleTestCase
from unittest.mock import Mock, patch

from cfnlint.context import create_context_for_template
from cfnlint.decode import decode_str
from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules.resources.ResourceType import ResourceType
from cfnlint.template import Template


class TestType(BaseRuleTestCase):
    """Test AWS Types"""

    def setUp(self):
        """Setup"""
        super(TestType, self).setUp()
        self.rule = ResourceType()

    def test_property_names(self):
        validator = CfnTemplateValidator({})
        errors = list(
            self.rule.validate(
                validator, "cfnResourceType", {"Type": "AWS::S3::Bucket"}, {}
            )
        )
        self.assertListEqual(
            errors,
            [],
            errors,
        )

    @patch("cfnlint.template.Template", autospec=True)
    def test_types_with_conditions(self, cfn):
        cfn = Mock()
        cfn.conditions = Mock()
        cfn.conditions.build_scenerios_on_region.return_value = [True]
        validator = CfnTemplateValidator({}).evolve(cfn=cfn)
        errors = list(
            self.rule.validate(
                validator,
                "cfnResources",
                {"Type": "Foo::Bar::Type", "Condition": "IsUsEast1"},
                {},
            )
        )

        self.assertListEqual(
            errors,
            [
                ValidationError(
                    "Resource type 'Foo::Bar::Type' does not exist in 'us-east-1'",
                    path=deque(["Type"]),
                    schema_path=deque([]),
                    rule=ResourceType(),
                ),
            ],
            errors,
        )

    @patch("cfnlint.template.Template", autospec=True)
    def test_types_with_conditions_false(self, cfn):
        cfn = Mock()
        cfn.conditions = Mock()
        cfn.conditions.build_scenerios_on_region.return_value = [False]
        validator = CfnTemplateValidator({}).evolve(cfn=cfn)
        errors = list(
            self.rule.validate(
                validator,
                "cfnResources",
                {"Type": "Foo::Bar::Type", "Condition": "IsUsEast1"},
                {},
            )
        )

        self.assertListEqual(errors, [], errors)

    @patch("cfnlint.template.Template", autospec=True)
    def test_types_with_conditions_false_and_true(self, cfn):
        cfn = Mock()
        cfn.conditions = Mock()
        cfn.conditions.build_scenerios_on_region.return_value = [True, False]
        validator = CfnTemplateValidator({}).evolve(cfn=cfn)
        errors = list(
            self.rule.validate(
                validator,
                "cfnResources",
                {"Type": "Foo::Bar::Type", "Condition": "IsUsEast1"},
                {},
            )
        )

        self.assertListEqual(
            errors,
            [
                ValidationError(
                    "Resource type 'Foo::Bar::Type' does not exist in 'us-east-1'",
                    path=deque(["Type"]),
                    schema_path=deque([]),
                    rule=ResourceType(),
                ),
            ],
            errors,
        )

    def test_types_with_partition_conditions(self):
        template = decode_str(
            """
        Conditions:
          IsChina: !Equals [!Ref AWS::Partition, "aws-cn"]
        Resources:
          ChinaOnly:
            Type: Foo::Bar::Type
            Condition: IsChina
        """
        )[0]
        cfn = Template("", template, ["us-east-1", "cn-north-1"])
        validator = CfnTemplateValidator({}).evolve(
            cfn=cfn, context=create_context_for_template(cfn)
        )
        errors = list(
            self.rule.validate(
                validator,
                "cfnResources",
                {"Type": "Foo::Bar::Type", "Condition": "IsChina"},
                {},
            )
        )

        self.assertListEqual(
            errors,
            [
                ValidationError(
                    "Resource type 'Foo::Bar::Type' does not exist in 'cn-north-1'",
                    path=deque(["Type"]),
                    schema_path=deque([]),
                    rule=ResourceType(),
                ),
            ],
            errors,
        )

    @patch("cfnlint.template.Template", autospec=True)
    def test_types_bad_sam_types(self, cfn):
        cfn = Mock()
        cfn.conditions = Mock()
        cfn.conditions.build_scenerios_on_region.return_value = [False]
        validator = CfnTemplateValidator({}).evolve(cfn=cfn)
        errors = list(
            self.rule.validate(
                validator,
                "cfnResources",
                {"Type": "AWS::Serverless::Foo"},
                {},
            )
        )

        self.assertListEqual(
            errors,
            [
                ValidationError(
                    (
                        "Resource type 'AWS::Serverless::Foo' "
                        "does not exist in 'us-east-1'"
                    ),
                    path=deque(["Type"]),
                    schema_path=deque([]),
                    rule=ResourceType(),
                ),
            ],
            errors,
        )
