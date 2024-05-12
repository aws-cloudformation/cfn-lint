"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.context import Context
from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules.jsonschema.CfnLint import CfnLint
from cfnlint.rules.jsonschema.CfnLintKeyword import CfnLintKeyword


class _FooError(CfnLintKeyword):
    id = "EXXXX"
    shortdesc = "A rule"
    description = "A rule"

    def __init__(self) -> None:
        super().__init__(["Foo"])

    def validate(self, validator, keywords, instance, schema):
        yield ValidationError("No Foo")


class _BarError(CfnLintKeyword):
    id = "EYYYY"
    shortdesc = "A rule"
    description = "A rule"

    def __init__(self) -> None:
        super().__init__(["Bar"])

    def validate(self, validator, keywords, instance, schema):
        yield ValidationError("No Bar", rule=self)


class _SubError(CfnLintKeyword):
    def __init__(self) -> None:
        super().__init__(["Bar"])


@pytest.fixture(scope="module")
def rule():
    rule = CfnLint()
    rule.child_rules["EXXXX"] = _FooError()
    rule.child_rules["EYYYY"] = _BarError()
    rule.child_rules["EZZZZ"] = _SubError()
    yield rule


@pytest.mark.parametrize(
    "name,keywords,expected_errs",
    [
        (
            "When no error in exception add it",
            ["Foo"],
            [
                ValidationError(
                    message="No Foo",
                    rule=_FooError(),
                ),
            ],
        ),
        (
            "When no error in exception add it",
            ["Foo", "Bar"],
            [
                ValidationError(
                    message="No Foo",
                    rule=_FooError(),
                ),
                ValidationError(
                    message="No Bar",
                    rule=_BarError(),
                ),
            ],
        ),
        (
            "When no error in exception add it",
            ["FooBar"],
            [],
        ),
    ],
)
def test_cfn_schema(name, keywords, expected_errs, rule):
    context = Context(regions=["us-east-1"])
    validator = CfnTemplateValidator(schema={}, context=context)

    errs = list(rule.cfnLint(validator, keywords, True, {}))
    assert errs == expected_errs, f"{name} failed {errs} did not match {expected_errs}"
