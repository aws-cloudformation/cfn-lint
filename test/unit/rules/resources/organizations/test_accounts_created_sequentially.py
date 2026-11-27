"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.unit.rules import BaseRuleTestCase

import pytest

from cfnlint.rules.resources.organizations.AccountsCreatedSequentially import (
    AccountsCreatedSequentially,
)


class TestAccountsCreatedSequentially(BaseRuleTestCase):
    """Test AWS::Organizations::Account resources are created sequentially"""

    def setUp(self):
        super(TestAccountsCreatedSequentially, self).setUp()
        self.collection.register(AccountsCreatedSequentially())
        self.success_templates = [
            "test/fixtures/templates/good/resources/organizations/accounts_created_sequentially.yaml",
        ]

    def test_file_positive(self):
        self.helper_file_positive()

    def test_file_negative(self):
        self.helper_file_negative(
            "test/fixtures/templates/bad/resources/organizations/accounts_created_sequentially.yaml",
            err_count=2,
        )


def _account(name, **attributes):
    return {
        "Type": "AWS::Organizations::Account",
        "Properties": {
            "AccountName": name,
            "Email": f"{name.lower()}@example.com",
        },
        **attributes,
    }


@pytest.fixture(scope="module")
def rule():
    rule = AccountsCreatedSequentially()
    yield rule


@pytest.mark.parametrize(
    "name,template,expected",
    [
        (
            "Single account",
            {"Resources": {"A": _account("A")}},
            [],
        ),
        (
            "Other resource types are ignored",
            {
                "Resources": {
                    "A": _account("A"),
                    "Bucket": {"Type": "AWS::S3::Bucket"},
                }
            },
            [],
        ),
        (
            "Two accounts without a dependency",
            {"Resources": {"A": _account("A"), "B": _account("B")}},
            [(["Resources", "B"], "'B' can be created at the same time as 'A'")],
        ),
        (
            "DependsOn as a string",
            {"Resources": {"A": _account("A"), "B": _account("B", DependsOn="A")}},
            [],
        ),
        (
            "DependsOn as a list, declared before the dependency",
            {"Resources": {"B": _account("B", DependsOn=["A"]), "A": _account("A")}},
            [],
        ),
        (
            "Dependency through Fn::GetAtt",
            {
                "Resources": {
                    "A": _account("A"),
                    "B": {
                        "Type": "AWS::Organizations::Account",
                        "Properties": {
                            "AccountName": {"Fn::GetAtt": ["A", "AccountId"]},
                            "Email": "b@example.com",
                        },
                    },
                }
            },
            [],
        ),
        (
            "Dependency through another resource",
            {
                "Resources": {
                    "A": _account("A"),
                    "Wait": {
                        "Type": "AWS::CloudFormation::WaitConditionHandle",
                        "DependsOn": "A",
                    },
                    "B": _account("B", DependsOn="Wait"),
                }
            },
            [],
        ),
        (
            "Chain is transitive",
            {
                "Resources": {
                    "A": _account("A"),
                    "B": _account("B", DependsOn="A"),
                    "C": _account("C", DependsOn="B"),
                }
            },
            [],
        ),
        (
            "Two accounts depending on the same account",
            {
                "Resources": {
                    "A": _account("A"),
                    "B": _account("B", DependsOn="A"),
                    "C": _account("C", DependsOn="A"),
                }
            },
            [(["Resources", "C"], "'C' can be created at the same time as 'B'")],
        ),
        (
            "Three independent accounts",
            {
                "Resources": {
                    "A": _account("A"),
                    "B": _account("B"),
                    "C": _account("C"),
                }
            },
            [
                (["Resources", "B"], "'B' can be created at the same time as 'A'"),
                (
                    ["Resources", "C"],
                    "'C' can be created at the same time as 'A', 'B'",
                ),
            ],
        ),
        (
            "Mutually exclusive conditions",
            {
                "Parameters": {"Env": {"Type": "String"}},
                "Conditions": {
                    "IsDev": {"Fn::Equals": [{"Ref": "Env"}, "dev"]},
                    "IsProd": {"Fn::Equals": [{"Ref": "Env"}, "prod"]},
                },
                "Resources": {
                    "A": _account("A", Condition="IsDev"),
                    "B": _account("B", Condition="IsProd"),
                },
            },
            [],
        ),
        (
            "Condition and its negation",
            {
                "Parameters": {"Env": {"Type": "String"}},
                "Conditions": {
                    "IsDev": {"Fn::Equals": [{"Ref": "Env"}, "dev"]},
                    "IsNotDev": {"Fn::Not": [{"Condition": "IsDev"}]},
                },
                "Resources": {
                    "A": _account("A", Condition="IsDev"),
                    "B": _account("B", Condition="IsNotDev"),
                },
            },
            [],
        ),
        (
            "Conditions that can both be true",
            {
                "Parameters": {
                    "Env": {"Type": "String"},
                    "Sandbox": {"Type": "String"},
                },
                "Conditions": {
                    "IsDev": {"Fn::Equals": [{"Ref": "Env"}, "dev"]},
                    "HasSandbox": {"Fn::Equals": [{"Ref": "Sandbox"}, "true"]},
                },
                "Resources": {
                    "A": _account("A", Condition="IsDev"),
                    "B": _account("B", Condition="HasSandbox"),
                },
            },
            [(["Resources", "B"], "'B' can be created at the same time as 'A'")],
        ),
        (
            "Same condition on both accounts",
            {
                "Parameters": {"Env": {"Type": "String"}},
                "Conditions": {
                    "IsDev": {"Fn::Equals": [{"Ref": "Env"}, "dev"]},
                },
                "Resources": {
                    "A": _account("A", Condition="IsDev"),
                    "B": _account("B", Condition="IsDev"),
                },
            },
            [(["Resources", "B"], "'B' can be created at the same time as 'A'")],
        ),
        (
            "Only one account has a condition",
            {
                "Parameters": {"Env": {"Type": "String"}},
                "Conditions": {
                    "IsDev": {"Fn::Equals": [{"Ref": "Env"}, "dev"]},
                },
                "Resources": {
                    "A": _account("A"),
                    "B": _account("B", Condition="IsDev"),
                },
            },
            [(["Resources", "B"], "'B' can be created at the same time as 'A'")],
        ),
        (
            "Unknown condition is left to other rules",
            {
                "Resources": {
                    "A": _account("A"),
                    "B": _account("B", Condition="Missing"),
                },
            },
            [],
        ),
    ],
    indirect=["template"],
)
def test_match(name, template, expected, rule, cfn):
    matches = rule.match(cfn)
    assert len(matches) == len(expected), f"Test {name!r} got {matches!r}"
    for match, (path, message) in zip(matches, expected):
        assert match.path == path, f"Test {name!r} got {match.path!r}"
        assert message in match.message, f"Test {name!r} got {match.message!r}"
