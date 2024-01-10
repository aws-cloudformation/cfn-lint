"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from __future__ import annotations

from copy import deepcopy
from test.unit.rules import BaseRuleTestCase
from typing import List
from unittest.mock import MagicMock, patch

from cfnlint.decode.cfn_json import Mark
from cfnlint.decode.node import dict_node, str_node
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


class RuleRefFunction(CloudFormationLintRule):
    """Test Rule"""

    id = "E3YYY"
    shortdesc = "Test Rule"
    description = "Test Rule"
    source_url = ""
    tags = []


class RuleFnIfFunction(CloudFormationLintRule):
    """Test Rule"""

    id = "E3AAAA"
    shortdesc = "Test Rule for Fn::IF function"
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
        self.template = build_dict(
            {
                build_str("Conditions"): build_dict(
                    {
                        build_str("IsUsEast1"): build_dict(
                            {
                                build_str("Fn::Equals"): [
                                    build_dict({build_str("Ref"): "AWS::Region"}),
                                    "us-east-1",
                                ]
                            }
                        ),
                        build_str("IsNotUsEast1"): build_dict(
                            {
                                build_str("Fn::Not"): [{"Condition": "IsUsEast1"}],
                            }
                        ),
                    }
                ),
                build_str("Resources"): build_dict(
                    {
                        build_str("Table"): build_dict(
                            {
                                build_str("Type"): "AWS::DynamoDB::Table",
                                build_str("Properties"): build_dict(
                                    {
                                        build_str("A"): [
                                            build_dict(
                                                {
                                                    "AttributeName": "pk",
                                                    "KeyType": "HASH",
                                                }
                                            ),
                                        ],
                                        build_str("B"): build_dict(
                                            {
                                                build_str("C"): "TTL",
                                                build_str("D"): True,
                                            }
                                        ),
                                        build_str("E"): "string",
                                        build_str("F"): 5,
                                        build_str("G"): ["A", "A"],
                                    }
                                ),
                            }
                        )
                    }
                ),
            },
        )
        self.rule.child_rules = {
            "E3XXX": RuleWithFunction(),
            "E3YYY": RuleWithOutFunction(),
            "E3ZZZ": RuleRefFunction(),
            "E3AAAA": RuleFnIfFunction(),
        }
        self.rule.rule_set = {
            "required": "E3XXX",
            "type": "E3YYY",
            "ref": "E3ZZZ",
            "fn_if": "E3AAAA",
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
        template["Resources"]["Table"]["Properties"] = build_dict({})

        self.cfn = Template("", template, ["us-east-1"])
        delattr(expected[0], "location")
        self.validate(schema, expected)

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
        self.template["Resources"]["Table"]["Properties"]["E"] = {
            build_str("Fn::If"): [
                "Condition",
                "string",
                {build_str("Ref"): "AWS::NoValue"},
            ]
        }
        self.cfn = Template("", self.template, ["us-east-1"])
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
                "E3ZZZ",
                "{'Ref': 'AWS::Region'} is not of type 'array' when 'Ref' is resolved",
                ["Resources", "Table", "Properties", "E", "Ref"],
            ),
        ]
        template = deepcopy(self.template)
        ref = {build_str("Ref"): "AWS::Region"}
        template["Resources"]["Table"]["Properties"]["E"] = ref

        self.cfn = Template("", template, ["us-east-1"])
        self.validate(schema, expected)

    def test_functions_properties_with_if(self):
        schema = {
            "properties": {
                "E": True,
            },
            "type": "object",
            "required": ["E"],
        }

        expected = [
            self.build_result(
                "E3XXX",
                "'E' is a required property",
                ["Resources", "Table", "Properties"],
            ),
        ]
        fn_if_1 = {
            build_str("Fn::If"): [
                "IsUsEast1",
                "string",
                build_dict({build_str("Ref"): "AWS::NoValue"}),
            ]
        }
        self.template["Resources"]["Table"]["Properties"]["E"] = fn_if_1

        self.cfn = Template("", self.template, ["us-east-1"])
        delattr(expected[0], "location")
        self.validate(schema, expected)

    def test_bad_types(self):
        schema = {
            "properties": {
                "E": True,
            },
            "type": "object",
            "required": ["E"],
        }

        self.cfn = Template(
            "", {"Resources": {"Table": {"Type": {"Foo": "Bar"}}}}, ["us-east-1"]
        )
        self.validate(schema, [])


def build_node(instance: str | dict, loc: str, type=str_node):
    return type(
        instance,
        Mark(f"{loc}-sm-line", f"{loc}-sm-column"),
        Mark(f"{loc}-em-line", f"{loc}-em-column"),
    )


def build_str(instance: str):
    return build_node(
        instance,
        instance,
        str_node,
    )


def build_dict(instance: dict):
    return build_node(
        instance,
        "object",
        dict_node,
    )
