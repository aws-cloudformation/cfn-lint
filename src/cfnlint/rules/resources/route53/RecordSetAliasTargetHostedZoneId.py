"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from collections import deque
from typing import Any, Iterator

from cfnlint.helpers import ensure_list, is_function
from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules.helpers import get_value_from_path
from cfnlint.rules.jsonschema.CfnLintKeyword import CfnLintKeyword

# Known resource attributes that return a HostedZoneId suitable for use as a
# Route53 AliasTarget.HostedZoneId. When a user references a different
# attribute on one of these resources, or uses Ref on an
# AWS::Route53::HostedZone, the value will not be a valid alias target zone.
_VALID_ALIAS_TARGET_ATTRIBUTES: dict[str, set[str]] = {
    "AWS::ElasticLoadBalancing::LoadBalancer": {"CanonicalHostedZoneNameID"},
    "AWS::ElasticLoadBalancingV2::LoadBalancer": {"CanonicalHostedZoneID"},
    "AWS::ApiGateway::DomainName": {
        "DistributionHostedZoneId",
        "RegionalHostedZoneId",
    },
    "AWS::ApiGatewayV2::DomainName": {"RegionalHostedZoneId"},
}


class RecordSetAliasTargetHostedZoneId(CfnLintKeyword):
    """Warn on suspicious AliasTarget.HostedZoneId references"""

    id = "W3046"
    shortdesc = "Validate Route53 AliasTarget HostedZoneId references"
    description = (
        "An AliasTarget HostedZoneId should reference the canonical hosted zone "
        "of the alias target (for example !GetAtt LoadBalancer.CanonicalHostedZoneID), "
        "not the hosted zone the record is being created in"
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-route53-aliastarget.html"
    tags = ["resources", "route53", "record_set"]

    def __init__(self) -> None:
        super().__init__(
            keywords=[
                "Resources/AWS::Route53::RecordSet/Properties",
                "Resources/AWS::Route53::RecordSetGroup/Properties/RecordSets/*",
            ],
        )

    def _check_value(
        self, validator: Validator, value: Any
    ) -> Iterator[ValidationError]:
        fn_k, fn_v = is_function(value)
        if fn_k is None:
            return

        if fn_k == "Ref":
            if not isinstance(fn_v, str):
                return
            resource = validator.context.resources.get(fn_v)
            if resource is not None and resource.type == "AWS::Route53::HostedZone":
                yield ValidationError(
                    (
                        f"{{'Ref': {fn_v!r}}} returns the Id of an "
                        "AWS::Route53::HostedZone, which is the hosted zone the "
                        "record is created in, not the alias target's canonical "
                        "hosted zone. Use !GetAtt on the alias target resource "
                        "instead (for example "
                        "!GetAtt LoadBalancer.CanonicalHostedZoneID)"
                    ),
                    rule=self,
                )
            return

        if fn_k == "Fn::GetAtt":
            parts = ensure_list(fn_v)
            if len(parts) == 1 and isinstance(parts[0], str):
                logical_id, _, attribute = parts[0].partition(".")
            elif len(parts) >= 2 and all(isinstance(p, str) for p in parts[:2]):
                logical_id, attribute = parts[0], parts[1]
            else:
                return

            if not attribute:
                return

            resource = validator.context.resources.get(logical_id)
            if resource is None:
                return

            valid_attrs = _VALID_ALIAS_TARGET_ATTRIBUTES.get(resource.type)
            if valid_attrs is None:
                return

            if attribute not in valid_attrs:
                expected = ", ".join(sorted(valid_attrs))
                yield ValidationError(
                    (
                        f"{{'Fn::GetAtt': [{logical_id!r}, {attribute!r}]}} "
                        f"does not return a HostedZoneId for {resource.type!r}. "
                        f"Expected one of: {expected}"
                    ),
                    rule=self,
                )

    def validate(
        self, validator: Validator, _, instance: Any, schema: Any
    ) -> ValidationResult:
        for hosted_zone_id, hosted_zone_id_validator in get_value_from_path(
            validator, instance, deque(["AliasTarget", "HostedZoneId"])
        ):
            if hosted_zone_id is None:
                continue
            for err in self._check_value(hosted_zone_id_validator, hosted_zone_id):
                yield err
