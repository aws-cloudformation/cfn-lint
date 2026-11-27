"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.api import lint
from cfnlint.rules.resources.sagemaker.HostingInstanceTypeEnum import (
    HostingInstanceTypeEnum,
)


@pytest.fixture(scope="module")
def rule():
    rule = HostingInstanceTypeEnum()
    yield rule


@pytest.fixture
def regions(request):
    return getattr(request, "param", ["us-east-1"])


@pytest.mark.parametrize(
    "regions,instance,expected_count",
    [
        # the reported value, in regions that offer it
        (["us-east-2"], "ml.m8g.large", 0),
        (["us-east-1"], "ml.m8g.large", 0),
        (["eu-west-1"], "ml.m8g.large", 0),
        (["us-east-2"], "ml.p5e.48xlarge", 0),
        # a region that does not offer it still reports
        (["ap-northeast-3"], "ml.m8g.large", 1),
        (["ap-northeast-2"], "ml.m8g.large", 1),
        (["us-west-1"], "ml.m8g.large", 1),
        # one finding for the region that lacks it, none for the one that has it
        (["us-east-1", "ap-northeast-3"], "ml.m8g.large", 1),
        # a size the API does not accept anywhere
        (["us-east-1"], "ml.m8g.32xlarge", 1),
        (["us-east-2"], "ml.m8g.32xlarge", 1),
        # a deprecated family the API no longer accepts
        (["us-east-1"], "ml.p3.2xlarge", 1),
        # a region absent from the enum is unconstrained
        (["eu-isoe-west-1"], "ml.m8g.large", 0),
    ],
    indirect=["regions"],
)
def test_validate(instance, expected_count, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))

    assert len(errs) == expected_count, (
        f"Expected {expected_count} errors got {len(errs)}: {errs}"
    )


_TEMPLATE = """AWSTemplateFormatVersion: "2010-09-09"
Parameters:
  Size:
    Type: String
Conditions:
  IsProd: !Equals [!Ref Size, prod]
Resources:
  Experiment:
    Type: AWS::SageMaker::InferenceExperiment
    Properties:
      Name: repro
      Type: ShadowMode
      RoleArn: arn:aws:iam::123456789012:role/repro
      EndpointName: reproendpoint
      ModelVariants:
        - ModelName: modela
          VariantName: VariantA
          InfrastructureConfig:
            InfrastructureType: RealTimeInference
            RealTimeInferenceConfig:
              InstanceCount: 1
%s
      ShadowModeConfig:
        SourceModelVariantName: VariantA
        ShadowModelVariants:
          - ShadowModelVariantName: VariantA
            SamplingPercentage: 50
"""


@pytest.mark.parametrize(
    "name,instance_type,expected_count",
    [
        ("absent", None, 0),
        ("ref_parameter", "              InstanceType: !Ref Size", 0),
        ("ref_pseudo", "              InstanceType: !Ref AWS::Region", 0),
        (
            "fn_if",
            "              InstanceType: !If [IsProd, ml.m8g.large, ml.m5.large]",
            0,
        ),
        ("fn_sub", "              InstanceType: !Sub ml.${Size}.large", 0),
        ("reported", "              InstanceType: ml.m8g.large", 0),
        # the same position with a bogus literal must report, so the silent
        # cases above are not silent because nothing reached the rule
        ("bogus_literal", "              InstanceType: ml.nosuch.large", 1),
        ("bad_size", "              InstanceType: ml.m8g.32xlarge", 1),
        # a non scalar is owned by the type rule; the enum reports it too,
        # which is unchanged by this PR
        ("non_scalar", "              InstanceType: []", 1),
    ],
)
def test_template(name, instance_type, expected_count):
    template = _TEMPLATE % ("" if instance_type is None else instance_type)
    matches = [m for m in lint(template, regions=["us-east-1"]) if m.rule.id == "E3642"]

    assert len(matches) == expected_count, (
        f"{name}: expected {expected_count} E3642 got {len(matches)}: {matches}"
    )
