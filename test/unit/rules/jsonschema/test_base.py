"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from collections import deque
from test.unit.rules import BaseRuleTestCase

from cfnlint.context import create_context_for_template
from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules import CloudFormationLintRule, RuleMatch
from cfnlint.rules.jsonschema.Base import BaseJsonSchema
from cfnlint.template import Template


class RuleWithFunction(CloudFormationLintRule):
    """Test Rule"""

    id = "E3XXX"
    shortdesc = "Test Rule"
    description = "Test Rule"
    source_url = ""
    tags: list[str] = []

    def bar(validator, bar, instance, schema):
        pass


class RuleWithOutFunction(CloudFormationLintRule):
    """Test Rule"""

    id = "E3YYY"
    shortdesc = "Test Rule"
    description = "Test Rule"
    source_url = ""
    tags: list[str] = []


class TestBaseJsonSchema(BaseRuleTestCase):
    """Test Base Json Schema"""

    def test_extend_validator(self):
        def _validator(validator, t, instance, schema):
            pass

        class Rule(BaseJsonSchema):
            def __init__(self) -> None:
                super().__init__()
                self.rule_set = {
                    "bar": "EXXXX",
                    "foobar": "EYYYY",
                }
                self.child_rules = {
                    "EXXXX": RuleWithFunction(),
                    "EYYYY": RuleWithOutFunction(),
                }
                self.validators = {
                    "foo": _validator,
                    "bar": None,
                    "foobar": None,
                }

        rule = Rule()

        cfn = Template("", {}, regions=["us-east-1"])

        validator = CfnTemplateValidator(True)
        validator = rule.extend_validator(
            validator,
            {},
            create_context_for_template(cfn),
        )

        self.assertEqual(validator.validators["foo"], _validator)
        self.assertIsNotNone(validator.validators["bar"])
        self.assertIsNone(validator.validators["foobar"])

    def test_json_Schema_validator(self):
        class Rule(BaseJsonSchema):
            id = "E3AAAA"

            def __init__(self) -> None:
                super().__init__()
                self.rule_set = {
                    "bar": "E3XXX",
                    "foobar": "E3YYY",
                    "foo": "E3ZZZ",
                }
                self.child_rules = {
                    "E3XXX": RuleWithFunction(),
                    "E3YYY": RuleWithOutFunction(),
                    "E3ZZZ": None,
                }
                self.validators = {
                    "bar": None,
                    "foobar": None,
                    "foo": None,
                }

        rule = Rule()

        validator = CfnTemplateValidator(True)

        def iter_errors(instance):
            yield ValidationError(
                "Failure1", path=deque(["A"]), extra_args={"Foo": "Bar"}
            )
            yield ValidationError(
                "Failure2", path=deque(["A"]), path_override=deque(["Test"])
            )
            yield ValidationError(
                "Failure3", path=deque(["A"]), rule=RuleWithFunction()
            )
            yield ValidationError("Failure4", path=deque(["A"]), validator="foobar")
            yield ValidationError("Failure5", path=deque(["A"]), validator="foo")

        validator.iter_errors = iter_errors

        errors = list(rule.json_schema_validate(validator, {}, []))
        # 5th error is ignored because the rule is None which means
        # the length is 4
        self.assertEqual(len(errors), 4)

        self.assertEqual(errors[0], RuleMatch(["A"], "Failure1"))
        self.assertEqual(errors[0].Foo, "Bar")
        self.assertEqual(errors[0].rule.id, "E3AAAA")
        self.assertEqual(errors[1], RuleMatch(["Test"], "Failure2"))
        self.assertEqual(errors[1].rule.id, "E3AAAA")
        self.assertEqual(errors[2], RuleMatch(["A"], "Failure3"))
        self.assertEqual(errors[2].rule.id, "E3XXX")
        self.assertEqual(errors[3], RuleMatch(["A"], "Failure4"))
        self.assertEqual(errors[3].rule.id, "E3YYY")

    def test_validate(self):
        class ChildRule(CloudFormationLintRule):
            id = "EXXXX"

        class Test(BaseJsonSchema):
            def __init__(self) -> None:
                super().__init__()
                self.rule_set = {"enum": "EXXXX"}
                self.child_rules = {"EXXXX": ChildRule()}

            @property
            def schema(self):
                return {
                    "type": "object",
                    "properties": {"foo": True, "bar": {"enum": ["foobar"]}},
                    "required": ["foo"],
                }

        validator = CfnTemplateValidator(True)
        rule = Test()

        errors = list(rule.validate(validator, {}, {"bar": "bad"}, []))
        self.assertListEqual(
            errors,
            [
                ValidationError(
                    "'foo' is a required property",
                    path=deque([]),
                    rule=Test(),
                    schema_path=deque(["required"]),
                    validator="required",
                    validator_value=["foo"],
                    instance={"bar": "bad"},
                ),
                ValidationError(
                    "'bad' is not one of ['foobar']",
                    path=deque(["bar"]),
                    rule=ChildRule(),
                    schema_path=deque(["properties", "bar", "enum"]),
                    validator="enum",
                    validator_value=["foobar"],
                    instance="bad",
                ),
            ],
        )
