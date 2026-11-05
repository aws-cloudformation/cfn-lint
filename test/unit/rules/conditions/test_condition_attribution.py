"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import cfnlint.decode.cfn_yaml  # pylint: disable=unused-import
import cfnlint.decode
from cfnlint import ConfigMixIn
from cfnlint.config import _DEFAULT_RULESDIR
from cfnlint.rules import Rules
from cfnlint.runner import run_template_by_data

# Regression test for https://github.com/aws-cloudformation/cfn-lint/issues/4880
# An undefined Condition name used to be reported under the enclosing rule
# (E8004 inside Fn::And, E8006 inside Fn::Or, E8005 inside Fn::Not, E8001 as
# a whole condition body), so E8007 could neither select nor suppress it.
# All four positions must report as E8007.
_TEMPLATE = """
AWSTemplateFormatVersion: "2010-09-09"
Parameters:
  Stage:
    Type: String
    Default: prod
Conditions:
  IsProd: !Equals [!Ref Stage, prod]
  InAnd:
    Fn::And:
      - Condition: NoSuchConditionA
      - Condition: IsProd
  InOr:
    Fn::Or:
      - Condition: NoSuchConditionB
      - Condition: IsProd
  InNot:
    Fn::Not:
      - Condition: NoSuchConditionC
  WholeBody:
    Condition: NoSuchConditionD
Resources:
  TopicA:
    Type: AWS::SNS::Topic
    Condition: InAnd
  TopicB:
    Type: AWS::SNS::Topic
    Condition: InOr
  TopicC:
    Type: AWS::SNS::Topic
    Condition: InNot
  TopicD:
    Type: AWS::SNS::Topic
    Condition: WholeBody
"""


def _run(template_str, **config_kwargs):
    (template, _) = cfnlint.decode.decode_str(template_str)
    rules = Rules.create_from_directory(_DEFAULT_RULESDIR)
    config = ConfigMixIn(
        regions=["us-east-1"],
        include_experimental=True,
        **config_kwargs,
    )
    return list(run_template_by_data(template=template, config=config, rules=rules))


def test_undefined_condition_names_reported_as_e8007():
    failures = _run(_TEMPLATE, include_checks=["I"])
    e800x = [(f.rule.id, f.message) for f in failures if f.rule.id.startswith("E800")]
    assert sorted(rule for rule, _ in e800x) == ["E8007"] * 4
    for name in [
        "NoSuchConditionA",
        "NoSuchConditionB",
        "NoSuchConditionC",
        "NoSuchConditionD",
    ]:
        assert any(name in message for _, message in e800x), name


def test_ignore_checks_e8007_suppresses_all_four():
    failures = _run(_TEMPLATE, include_checks=["I"], ignore_checks=["E8007"])
    assert [f.rule.id for f in failures if f.rule.id.startswith("E800")] == []


def test_defined_condition_names_report_no_e800x():
    template = _TEMPLATE.replace("NoSuchConditionA", "IsProd")
    template = template.replace("NoSuchConditionB", "IsProd")
    template = template.replace("NoSuchConditionC", "IsProd")
    template = template.replace("NoSuchConditionD", "IsProd")
    failures = _run(template, include_checks=["I"])
    assert [f.rule.id for f in failures if f.rule.id.startswith("E800")] == []


def test_enclosing_rules_still_report_their_own_errors():
    # The fix must not swallow genuine Fn::And / Fn::Not structure errors.
    template = """
AWSTemplateFormatVersion: "2010-09-09"
Parameters:
  Stage:
    Type: String
    Default: prod
Conditions:
  IsProd: !Equals [!Ref Stage, prod]
  BadAnd:
    Fn::And:
      - Condition: IsProd
  BadNot:
    Fn::Not:
      - Condition: IsProd
      - Condition: IsProd
Resources:
  TopicA:
    Type: AWS::SNS::Topic
    Condition: BadAnd
"""
    failures = _run(template, include_checks=["I"])
    ids = [f.rule.id for f in failures if f.rule.id.startswith("E800")]
    assert "E8004" in ids
    assert "E8005" in ids
    assert "E8007" not in ids
