"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from test.unit.rules import BaseRuleTestCase

from cfnlint._typing import Path
from cfnlint.decode.cfn_json import Mark
from cfnlint.decode.node import dict_node, str_node
from cfnlint.rules import CloudFormationLintRule, RuleMatch
from cfnlint.rules.jsonschema.JsonSchema import JsonSchema
from cfnlint.template import Template


class RuleWithFunction(CloudFormationLintRule):
    """Test Rule"""

    id = "E3XXX"
    shortdesc = "Test Rule"
    description = "Test Rule"
    source_url = ""
    tags: list[str] = []


class RuleWithOutFunction(CloudFormationLintRule):
    """Test Rule"""

    id = "E3YYY"
    shortdesc = "Test Rule"
    description = "Test Rule"
    source_url = ""
    tags: list[str] = []


class RuleRefFunction(CloudFormationLintRule):
    """Test Rule"""

    id = "E3YYY"
    shortdesc = "Test Rule"
    description = "Test Rule"
    source_url = ""
    tags: list[str] = []


class RuleFnIfFunction(CloudFormationLintRule):
    """Test Rule"""

    id = "E3AAAA"
    shortdesc = "Test Rule for Fn::IF function"
    description = "Test Rule"
    source_url = ""
    tags: list[str] = []


class TestJsonSchema(BaseRuleTestCase):
    """Test Json Size"""

    def setUp(self):
        """Setup"""
        super(TestJsonSchema, self).setUp()
        self.maxDiff = None
        self.rule = JsonSchema()
        self.template = build_dict({})
        self.cfn = Template("", self.template, ["us-east-1"])

    def build_result(self, message: str, path: Path) -> RuleMatch:
        if len(path) > 0:
            return RuleMatch(
                path[:],
                message,
                rule=self.rule,
                location=(
                    f"{path[-1]}-sm-line",
                    f"{path[-1]}-sm-column",
                    f"{path[-1]}-em-line",
                    f"{path[-1]}-em-column",
                ),
            )

        return RuleMatch(path[:], message, rule=self.rule, location=(1, 1, 1, 1))

    def validate(self, expected):
        matches = self.rule.match(self.cfn)

        self.assertListEqual(
            list(map(vars, expected)),
            list(map(vars, matches)),
            list(map(vars, matches)),
        )

    def test_required_properties(self):
        expected = [
            self.build_result(
                "'Resources' is a required property",
                [],
            ),
        ]

        self.cfn = Template("", build_dict({}), ["us-east-1"])
        delattr(expected[0], "location")
        self.validate(expected)

    def test_extra(self):
        expected = [
            self.build_result(
                "Additional properties are not allowed ('Foo' was unexpected)",
                ["Foo"],
            ),
        ]
        self.cfn = Template(
            "",
            build_dict(
                {
                    build_str("Resources"): build_dict({}),
                    build_str("Foo"): build_dict({}),
                },
            ),
            ["us-east-1"],
        )
        self.validate(expected)

    def test_config(self):
        self.rule.config["sections"] = "Foo"
        self.cfn = Template(
            "",
            build_dict(
                {
                    build_str("Resources"): build_dict({}),
                    build_str("Foo"): build_dict({}),
                },
            ),
            ["us-east-1"],
        )
        self.validate([])


def build_node(instance: str | dict, loc: str, type=str_node):
    return type(
        instance,
        Mark(f"{loc}-sm-line", f"{loc}-sm-column"),  # type: ignore
        Mark(f"{loc}-em-line", f"{loc}-em-column"),  # type: ignore
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
