"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.route53.RecordSetAliasTargetHostedZoneId import (
    RecordSetAliasTargetHostedZoneId,
)


@pytest.fixture(scope="module")
def rule():
    return RecordSetAliasTargetHostedZoneId()


@pytest.fixture
def template():
    return {
        "Resources": {
            "MyHostedZone": {"Type": "AWS::Route53::HostedZone"},
            "MyClassicElb": {"Type": "AWS::ElasticLoadBalancing::LoadBalancer"},
            "MyAlb": {"Type": "AWS::ElasticLoadBalancingV2::LoadBalancer"},
            "MyApiDomain": {"Type": "AWS::ApiGateway::DomainName"},
            "MyHttpApiDomain": {"Type": "AWS::ApiGatewayV2::DomainName"},
            "MyBucket": {"Type": "AWS::S3::Bucket"},
        },
    }


def _props(hosted_zone_id):
    return {
        "AliasTarget": {
            "DNSName": "example.com",
            "HostedZoneId": hosted_zone_id,
        },
    }


@pytest.mark.parametrize(
    "name,instance,expect_error",
    [
        ("Static string is not flagged", _props("Z2FDTNDATAQYW2"), False),
        (
            "Ref to AWS::Route53::HostedZone is flagged",
            _props({"Ref": "MyHostedZone"}),
            True,
        ),
        (
            "Ref to an unrelated resource is not flagged",
            _props({"Ref": "MyBucket"}),
            False,
        ),
        (
            "Ref to a parameter or unknown name is not flagged",
            _props({"Ref": "SomeParameter"}),
            False,
        ),
        (
            "GetAtt classic ELB CanonicalHostedZoneNameID is not flagged",
            _props({"Fn::GetAtt": ["MyClassicElb", "CanonicalHostedZoneNameID"]}),
            False,
        ),
        (
            "GetAtt classic ELB DNSName is flagged (wrong attribute)",
            _props({"Fn::GetAtt": ["MyClassicElb", "DNSName"]}),
            True,
        ),
        (
            "GetAtt ALB CanonicalHostedZoneID is not flagged",
            _props({"Fn::GetAtt": ["MyAlb", "CanonicalHostedZoneID"]}),
            False,
        ),
        (
            "GetAtt ALB DNSName is flagged (wrong attribute)",
            _props({"Fn::GetAtt": ["MyAlb", "DNSName"]}),
            True,
        ),
        (
            "GetAtt API Gateway DistributionHostedZoneId is not flagged",
            _props({"Fn::GetAtt": ["MyApiDomain", "DistributionHostedZoneId"]}),
            False,
        ),
        (
            "GetAtt API Gateway RegionalHostedZoneId is not flagged",
            _props({"Fn::GetAtt": ["MyApiDomain", "RegionalHostedZoneId"]}),
            False,
        ),
        (
            "GetAtt API Gateway DistributionDomainName is flagged",
            _props({"Fn::GetAtt": ["MyApiDomain", "DistributionDomainName"]}),
            True,
        ),
        (
            "GetAtt HTTP API RegionalHostedZoneId is not flagged",
            _props({"Fn::GetAtt": ["MyHttpApiDomain", "RegionalHostedZoneId"]}),
            False,
        ),
        (
            "GetAtt to an unrelated resource is not flagged",
            _props({"Fn::GetAtt": ["MyBucket", "DomainName"]}),
            False,
        ),
        (
            "GetAtt to an unknown resource is not flagged",
            _props({"Fn::GetAtt": ["Missing", "CanonicalHostedZoneID"]}),
            False,
        ),
        (
            "GetAtt with dotted string form is supported",
            _props({"Fn::GetAtt": "MyAlb.CanonicalHostedZoneID"}),
            False,
        ),
        (
            "GetAtt with dotted string form catches wrong attribute",
            _props({"Fn::GetAtt": "MyAlb.DNSName"}),
            True,
        ),
        (
            "Fn::ImportValue is not flagged",
            _props({"Fn::ImportValue": "SomeExport"}),
            False,
        ),
        (
            "Properties without AliasTarget is not flagged",
            {"HostedZoneId": {"Ref": "MyHostedZone"}, "Name": "foo", "Type": "A"},
            False,
        ),
        (
            "Ref with non-string value is not flagged",
            _props({"Ref": ["MyHostedZone"]}),
            False,
        ),
        (
            "GetAtt with malformed parts is not flagged",
            _props({"Fn::GetAtt": [123, 456]}),
            False,
        ),
        (
            "GetAtt single string without dot is not flagged",
            _props({"Fn::GetAtt": "MyAlb"}),
            False,
        ),
    ],
)
def test_validate(name, instance, expect_error, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))

    if expect_error:
        assert len(errs) == 1, f"Test {name!r}: expected 1 error, got {errs!r}"
        assert isinstance(errs[0], ValidationError)
        assert errs[0].rule == rule
    else:
        assert errs == [], f"Test {name!r}: expected no errors, got {errs!r}"
