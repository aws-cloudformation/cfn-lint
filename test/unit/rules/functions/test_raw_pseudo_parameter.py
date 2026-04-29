"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.context import create_context_for_template
from cfnlint.jsonschema import CfnTemplateValidator, ValidationError
from cfnlint.rules.functions.RawPseudoParameter import RawPseudoParameter
from cfnlint.template import Template


@pytest.fixture(scope="module")
def rule():
    rule = RawPseudoParameter()
    yield rule


@pytest.fixture(scope="module")
def cfn():
    return Template(
        "",
        {},
        regions=["us-east-1"],
    )


@pytest.fixture(scope="module")
def context(cfn):
    return create_context_for_template(cfn)


@pytest.mark.parametrize(
    "name,instance,expected",
    [
        (
            "Invalid - raw AWS::NoValue",
            "AWS::NoValue",
            [
                ValidationError(
                    (
                        "'AWS::NoValue' is a pseudo-parameter and should "
                        "probably be used as 'Ref: AWS::NoValue' "
                        "instead of a plain string"
                    ),
                    rule=RawPseudoParameter(),
                ),
            ],
        ),
        (
            "Invalid - raw AWS::Region",
            "AWS::Region",
            [
                ValidationError(
                    (
                        "'AWS::Region' is a pseudo-parameter and should "
                        "probably be used as 'Ref: AWS::Region' "
                        "instead of a plain string"
                    ),
                    rule=RawPseudoParameter(),
                ),
            ],
        ),
        (
            "Invalid - raw AWS::AccountId",
            "AWS::AccountId",
            [
                ValidationError(
                    (
                        "'AWS::AccountId' is a pseudo-parameter and should "
                        "probably be used as 'Ref: AWS::AccountId' "
                        "instead of a plain string"
                    ),
                    rule=RawPseudoParameter(),
                ),
            ],
        ),
        (
            "Invalid - raw AWS::Partition",
            "AWS::Partition",
            [
                ValidationError(
                    (
                        "'AWS::Partition' is a pseudo-parameter and should "
                        "probably be used as 'Ref: AWS::Partition' "
                        "instead of a plain string"
                    ),
                    rule=RawPseudoParameter(),
                ),
            ],
        ),
        (
            "Invalid - raw AWS::StackName",
            "AWS::StackName",
            [
                ValidationError(
                    (
                        "'AWS::StackName' is a pseudo-parameter and should "
                        "probably be used as 'Ref: AWS::StackName' "
                        "instead of a plain string"
                    ),
                    rule=RawPseudoParameter(),
                ),
            ],
        ),
        (
            "Invalid - raw AWS::StackId",
            "AWS::StackId",
            [
                ValidationError(
                    (
                        "'AWS::StackId' is a pseudo-parameter and should "
                        "probably be used as 'Ref: AWS::StackId' "
                        "instead of a plain string"
                    ),
                    rule=RawPseudoParameter(),
                ),
            ],
        ),
        (
            "Invalid - raw AWS::URLSuffix",
            "AWS::URLSuffix",
            [
                ValidationError(
                    (
                        "'AWS::URLSuffix' is a pseudo-parameter and should "
                        "probably be used as 'Ref: AWS::URLSuffix' "
                        "instead of a plain string"
                    ),
                    rule=RawPseudoParameter(),
                ),
            ],
        ),
        (
            "Invalid - raw AWS::NotificationARNs",
            "AWS::NotificationARNs",
            [
                ValidationError(
                    (
                        "'AWS::NotificationARNs' is a pseudo-parameter and should "
                        "probably be used as 'Ref: AWS::NotificationARNs' "
                        "instead of a plain string"
                    ),
                    rule=RawPseudoParameter(),
                ),
            ],
        ),
    ],
)
def test_validate(name, instance, expected, rule, context, cfn):
    validator = CfnTemplateValidator(context=context, cfn=cfn)
    errs = list(rule.rawPseudoParameter(validator, {}, instance, {}))
    assert errs == expected, f"Test {name!r} got {errs!r}"
