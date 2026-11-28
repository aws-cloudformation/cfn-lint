"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.api import lint
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.lmbd.FunctionEnvironmentSize import FunctionEnvironmentSize


@pytest.fixture(scope="module")
def rule():
    rule = FunctionEnvironmentSize()
    yield rule


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            {"FOO": "bar"},
            [],
        ),
        (
            {},
            [],
        ),
        (
            # 4096 bytes of key and value, but 4103 as compact JSON
            {"A" * 2048: "B" * 2048},
            [
                ValidationError(
                    "Lambda environment variables total size (4103) "
                    "exceeds the 4 KB (4096 bytes) limit",
                    rule=FunctionEnvironmentSize(),
                ),
            ],
        ),
        (
            {"A" * 2048: "B" * 2049},
            [
                ValidationError(
                    "Lambda environment variables total size (4104) "
                    "exceeds the 4 KB (4096 bytes) limit",
                    rule=FunctionEnvironmentSize(),
                ),
            ],
        ),
        (
            # Exactly 4096 bytes as compact JSON stays silent
            {"K" * 2044: "V" * 2045},
            [],
        ),
        (
            # One byte over the limit as compact JSON
            {"K" * 2044: "V" * 2046},
            [
                ValidationError(
                    "Lambda environment variables total size (4097) "
                    "exceeds the 4 KB (4096 bytes) limit",
                    rule=FunctionEnvironmentSize(),
                ),
            ],
        ),
        (
            # 100 variables: 3500 bytes of key and value, 4101 as
            # compact JSON (the 6n + 1 structural overhead matters)
            {f"V{i:03d}": "a" * 31 for i in range(100)},
            [
                ValidationError(
                    "Lambda environment variables total size (4101) "
                    "exceeds the 4 KB (4096 bytes) limit",
                    rule=FunctionEnvironmentSize(),
                ),
            ],
        ),
        (
            {f"KEY{i}": "x" * 100 for i in range(50)},
            [
                ValidationError(
                    "Lambda environment variables total size (5541) "
                    "exceeds the 4 KB (4096 bytes) limit",
                    rule=FunctionEnvironmentSize(),
                ),
            ],
        ),
        (
            # Non-ASCII values count as UTF-8 bytes, not escape sequences
            {"K": "é"},
            [],
        ),
        (
            # JSON escaping (quotes) counts toward the limit
            {"K": 'a"b'},
            [],
        ),
        (
            "not-an-object",
            [],
        ),
        (
            {"KEY": 12345},
            [],
        ),
        (
            {"KEY": ["a", "b"]},
            [],
        ),
    ],
)
def test_validate(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "LambdaRuntime", instance, {}))
    assert errs == expected, f"Expected {expected} got {errs}"


@pytest.mark.parametrize(
    "name,instance,template,expected",
    [
        (
            "Fn::Join under limit",
            {
                **{f"V{i}": "a" * 700 for i in range(1, 5)},
                "V5": {"Fn::Join": ["", ["a" * 700]]},
            },
            {},
            [],
        ),
        (
            "Fn::Join literal over limit",
            {
                **{f"V{i}": "a" * 1000 for i in range(1, 5)},
                "V5": {"Fn::Join": ["", ["a" * 1000]]},
            },
            {},
            [
                ValidationError(
                    "Lambda environment variables total size (5041) "
                    "exceeds the 4 KB (4096 bytes) limit",
                    rule=FunctionEnvironmentSize(),
                ),
            ],
        ),
        (
            "Fn::Join multi-byte UTF-8 over limit",
            {"K": {"Fn::Join": ["", ["é" * 2100]]}},
            {},
            [
                ValidationError(
                    "Lambda environment variables total size (4208) "
                    "exceeds the 4 KB (4096 bytes) limit",
                    rule=FunctionEnvironmentSize(),
                ),
            ],
        ),
        (
            "Fn::Join mixing literal and unresolved Ref",
            {
                **{f"V{i}": "a" * 1000 for i in range(1, 5)},
                "V5": {"Fn::Join": ["", ["a" * 1000, {"Ref": "UnboundParam"}]]},
            },
            {"Parameters": {"UnboundParam": {"Type": "String"}}},
            [
                ValidationError(
                    "Lambda environment variables total size (5041) "
                    "exceeds the 4 KB (4096 bytes) limit",
                    rule=FunctionEnvironmentSize(),
                ),
            ],
        ),
        (
            "Fn::Sub literal over limit",
            {
                **{f"V{i}": "a" * 1000 for i in range(1, 5)},
                "V5": {"Fn::Sub": "a" * 1000},
            },
            {},
            [
                ValidationError(
                    "Lambda environment variables total size (5041) "
                    "exceeds the 4 KB (4096 bytes) limit",
                    rule=FunctionEnvironmentSize(),
                ),
            ],
        ),
        (
            "Fn::Sub with literal escape and unresolved param over limit",
            {
                "BIG": {
                    "Fn::Sub": ("prefix-${!Escaped}-${UnboundParam}-" + ("a" * 4080))
                },
            },
            {"Parameters": {"UnboundParam": {"Type": "String"}}},
            [
                ValidationError(
                    "Lambda environment variables total size (4109) "
                    "exceeds the 4 KB (4096 bytes) limit",
                    rule=FunctionEnvironmentSize(),
                ),
            ],
        ),
        (
            "Fn::Sub with mapping parameter over limit",
            {
                "BIG": {"Fn::Sub": ["${Part}", {"Part": "a" * 4100}]},
            },
            {},
            [
                ValidationError(
                    "Lambda environment variables total size (4110) "
                    "exceeds the 4 KB (4096 bytes) limit",
                    rule=FunctionEnvironmentSize(),
                ),
            ],
        ),
        (
            "Ref entries with empty Default still count keys and JSON overhead",
            {f"{'K' * 50}{i:03d}": {"Ref": "P"} for i in range(100)},
            {"Parameters": {"P": {"Type": "String", "Default": ""}}},
            [
                ValidationError(
                    "Lambda environment variables total size (5901) "
                    "exceeds the 4 KB (4096 bytes) limit",
                    rule=FunctionEnvironmentSize(),
                ),
            ],
        ),
        (
            "Ref entries without Default count keys and JSON overhead",
            {f"{'K' * 50}{i:03d}": {"Ref": "P"} for i in range(100)},
            {"Parameters": {"P": {"Type": "String"}}},
            [
                ValidationError(
                    "Lambda environment variables total size (5901) "
                    "exceeds the 4 KB (4096 bytes) limit",
                    rule=FunctionEnvironmentSize(),
                ),
            ],
        ),
        (
            "Unresolvable Fn::GetAtt entries count keys and JSON overhead",
            {f"{'K' * 50}{i:03d}": {"Fn::GetAtt": ["Role", "Arn"]} for i in range(100)},
            {},
            [
                ValidationError(
                    "Lambda environment variables total size (5901) "
                    "exceeds the 4 KB (4096 bytes) limit",
                    rule=FunctionEnvironmentSize(),
                ),
            ],
        ),
        (
            "Fn::If both branches over limit reports single error",
            {
                **{f"V{i}": "a" * 1000 for i in range(1, 5)},
                "V5": {"Fn::If": ["Cond", "a" * 1000, "a" * 1000]},
            },
            {
                "Parameters": {"Env": {"Type": "String"}},
                "Conditions": {"Cond": {"Fn::Equals": [{"Ref": "Env"}, "prod"]}},
            },
            [
                ValidationError(
                    "Lambda environment variables total size (5041) "
                    "exceeds the 4 KB (4096 bytes) limit",
                    rule=FunctionEnvironmentSize(),
                ),
            ],
        ),
        (
            "Fn::If mutually exclusive branches stay under limit",
            {
                "V1": {"Fn::If": ["Cond", "a" * 3000, "b"]},
                "V2": {"Fn::If": ["Cond", "b", "a" * 3000]},
            },
            {
                "Parameters": {"Env": {"Type": "String"}},
                "Conditions": {"Cond": {"Fn::Equals": [{"Ref": "Env"}, "prod"]}},
            },
            [],
        ),
        (
            "Fn::If with one oversized branch catches excess",
            {
                **{f"V{i}": "a" * 800 for i in range(1, 5)},
                "V5": {"Fn::If": ["Cond", "ok", "a" * 1000]},
            },
            {
                "Parameters": {"Env": {"Type": "String"}},
                "Conditions": {"Cond": {"Fn::Equals": [{"Ref": "Env"}, "prod"]}},
            },
            [
                ValidationError(
                    "Lambda environment variables total size (4241) "
                    "exceeds the 4 KB (4096 bytes) limit",
                    rule=FunctionEnvironmentSize(),
                ),
            ],
        ),
        (
            "Ref AWS::NoValue omits entry from size calculation",
            {
                **{f"V{i}": "a" * 1000 for i in range(1, 5)},
                "V5": {"Fn::If": ["Cond", {"Ref": "AWS::NoValue"}, "a" * 1000]},
                "V6": {"Ref": "AWS::NoValue"},
            },
            {
                "Parameters": {"Env": {"Type": "String"}},
                "Conditions": {"Cond": {"Fn::Equals": [{"Ref": "Env"}, "prod"]}},
            },
            [
                ValidationError(
                    "Lambda environment variables total size (5041) "
                    "exceeds the 4 KB (4096 bytes) limit",
                    rule=FunctionEnvironmentSize(),
                ),
            ],
        ),
        (
            "Nested Fn::If inside Fn::Join resolves branches",
            {
                **{f"V{i}": "a" * 1000 for i in range(1, 5)},
                "V5": {
                    "Fn::Join": [
                        "",
                        [{"Fn::If": ["Cond", "a" * 1000, "a" * 1000]}],
                    ]
                },
            },
            {
                "Parameters": {"Env": {"Type": "String"}},
                "Conditions": {"Cond": {"Fn::Equals": [{"Ref": "Env"}, "prod"]}},
            },
            [
                ValidationError(
                    "Lambda environment variables total size (5041) "
                    "exceeds the 4 KB (4096 bytes) limit",
                    rule=FunctionEnvironmentSize(),
                ),
            ],
        ),
    ],
)
def test_validate_intrinsics(name, instance, template, expected, rule, validator):
    errs = list(rule.validate(validator, "LambdaRuntime", instance, {}))
    assert errs == expected, f"{name}: expected {expected} got {errs}"


def test_lint_end_to_end_intrinsics():
    a = "a" * 1000
    tmpl = f"""AWSTemplateFormatVersion: "2010-09-09"
Parameters:
  P:
    Type: String
    Default: ""
Resources:
  Role:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal: {{Service: lambda.amazonaws.com}}
            Action: sts:AssumeRole
  FnJoin:
    Type: AWS::Lambda::Function
    Properties:
      Role: !GetAtt Role.Arn
      Code: {{ZipFile: "x"}}
      Handler: index.handler
      Runtime: python3.12
      Environment:
        Variables:
          V1: {a}
          V2: {a}
          V3: {a}
          V4: {a}
          V5: !Join ["", ["{a}"]]
  FnRefs:
    Type: AWS::Lambda::Function
    Properties:
      Role: !GetAtt Role.Arn
      Code: {{ZipFile: "x"}}
      Handler: index.handler
      Runtime: python3.12
      Environment:
        Variables:
""" + "".join(f"          {'K' * 50}{i:03d}: !Ref P\n" for i in range(100))

    matches = sorted((m.message for m in lint(tmpl) if m.rule.id == "E3697"))
    assert matches == [
        (
            "Lambda environment variables total size (5041) "
            "exceeds the 4 KB (4096 bytes) limit"
        ),
        (
            "Lambda environment variables total size (5901) "
            "exceeds the 4 KB (4096 bytes) limit"
        ),
    ]
