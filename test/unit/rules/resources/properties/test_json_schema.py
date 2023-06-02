"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from copy import deepcopy
from test.unit.rules import BaseRuleTestCase
from typing import List
from unittest.mock import MagicMock, patch

from cfnlint.decode.cfn_json import Mark
from cfnlint.decode.node import str_node
from cfnlint.rules import CloudFormationLintRule, RuleMatch
from cfnlint.rules.resources.properties.JsonSchema import (
    PROVIDER_SCHEMA_MANAGER,
    JsonSchema,
)
from cfnlint.template import Template


class RuleWithFunction(CloudFormationLintRule):
    """Test Rule"""

    id = "E3XXX"
    shortdesc = "Test Rule"
    description = "Test Rule"
    source_url = ""
    tags = []


class RuleWithOutFunction(CloudFormationLintRule):
    """Test Rule"""

    id = "E3YYY"
    shortdesc = "Test Rule"
    description = "Test Rule"
    source_url = ""
    tags = []


class TestJsonSchema(BaseRuleTestCase):
    """Test Json Size"""

    def setUp(self):
        """Setup"""
        super(TestJsonSchema, self).setUp()
        self.maxDiff = None
        self.rule = JsonSchema()
        self.template = {
            build_key("Resources"): {
                build_key("Table"): {
                    build_key("Type"): "AWS::DynamoDB::Table",
                    build_key("Properties"): {
                        build_key("A"): [{"AttributeName": "pk", "KeyType": "HASH"}],
                        build_key("B"): {
                            build_key("C"): "TTL",
                            build_key("D"): True,
                        },
                        build_key("E"): "string",
                        build_key("F"): 5,
                        build_key("G"): ["A", "A"],
                    },
                }
            }
        }
        self.rule.child_rules = {
            "E3XXX": RuleWithFunction(),
            "E3YYY": RuleWithOutFunction(),
        }
        self.rule.rule_set = {
            "required": "E3XXX",
            "type": "E3YYY",
        }

        self.cfn = Template("", self.template, ["us-east-1"])

    def build_result(self, rule_id: str, message: str, path: List[str]) -> RuleMatch:
        return RuleMatch(
            path[:],
            message,
            rule=self.rule.child_rules.get(rule_id),
            location=(
                f"{path[-1]}-sm-line",
                f"{path[-1]}-sm-column",
                f"{path[-1]}-em-line",
                f"{path[-1]}-em-column",
            ),
        )

    def validate(self, schema, expected, object=None):
        with patch.object(
            PROVIDER_SCHEMA_MANAGER, "get_resource_schema", return_value=None
        ) as mock_method:
            resource_schema = MagicMock()
            resource_schema.json_schema = schema
            resource_schema.is_cached = False
            mock_method.return_value = resource_schema
            matches = self.rule.match(self.cfn)

            self.assertListEqual(
                list(map(vars, expected)),
                list(map(vars, matches)),
                list(map(vars, matches)),
            )

    def test_required_empty(self):
        schema = {
            "properties": {
                "A": {
                    "type": "string",
                },
            },
            "required": ["A"],
        }

        expected = [
            self.build_result(
                "E3XXX",
                "'A' is a required property",
                ["Resources", "Table", "Properties"],
            ),
        ]

        template = deepcopy(self.template)
        template["Resources"]["Table"]["Properties"] = {}

        self.cfn = Template("", template, ["us-east-1"])
        delattr(expected[0], "location")
        self.validate(schema, expected, {})

    def test_type(self):
        schema = {
            "properties": {
                "E": {
                    "type": "array",
                },
            },
        }

        expected = [
            self.build_result(
                "E3YYY",
                "'string' is not of type 'array'",
                ["Resources", "Table", "Properties", "E"],
            ),
        ]

        self.validate(schema, expected)

    def test_functions_if(self):
        schema = {
            "properties": {
                "E": {
                    "type": "array",
                },
            },
        }

        expected = [
            self.build_result(
                "E3YYY",
                "'string' is not of type 'array'",
                ["Resources", "Table", "Properties", "E", "Fn::If", 1],
            ),
        ]
        template = deepcopy(self.template)
        template["Resources"]["Table"]["Properties"]["E"] = {
            build_key("Fn::If"): [
                "Condition",
                "string",
                {build_key("Ref"): "AWS::NoValue"},
            ]
        }
        self.cfn = Template("", template, ["us-east-1"])
        delattr(expected[0], "location")
        self.validate(schema, expected)

    def test_functions_ref(self):
        schema = {
            "properties": {
                "E": {
                    "type": "array",
                },
            },
        }

        expected = [
            self.build_result(
                "E3YYY",
                "{'Ref': 'AWS::Region'} is not of type 'array'",
                ["Resources", "Table", "Properties", "E", "Ref"],
            ),
        ]
        template = deepcopy(self.template)
        ref = {build_key("Ref"): "AWS::Region"}
        template["Resources"]["Table"]["Properties"]["E"] = ref

        self.cfn = Template("", template, ["us-east-1"])
        self.validate(schema, expected)


def build_key(key: str):
    return str_node(
        key,
        Mark(f"{key}-sm-line", f"{key}-sm-column"),
        Mark(f"{key}-em-line", f"{key}-em-column"),
    )
