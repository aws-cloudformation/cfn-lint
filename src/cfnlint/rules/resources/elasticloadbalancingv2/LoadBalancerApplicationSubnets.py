"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import re
from typing import Any

import cfnlint.data.schemas.extensions.aws_elasticloadbalancingv2_loadbalancer
from cfnlint.helpers import is_function
from cfnlint.jsonschema import ValidationResult, Validator
from cfnlint.rules.jsonschema.CfnLintJsonSchema import CfnLintJsonSchema, SchemaDetails

# Local Zone names add a location code to the region name (us-west-2-lax-1a).
# Availability Zone names don't (us-west-2a).
_LOCAL_ZONE = re.compile(r"^[a-z]{2}(-[a-z]+)+-\d+-[a-z]+-\d+[a-z]$")


class LoadBalancerApplicationSubnets(CfnLintJsonSchema):
    id = "E3680"
    shortdesc = "Application load balancers require at least 2 subnets"
    description = (
        "Application load balancers require at least 2 subnets, "
        "unless the subnets are in a Local Zone"
    )
    tags = ["resources"]

    def __init__(self) -> None:
        super().__init__(
            keywords=[
                "Resources/AWS::ElasticLoadBalancingV2::LoadBalancer/Properties",
            ],
            schema_details=SchemaDetails(
                module=cfnlint.data.schemas.extensions.aws_elasticloadbalancingv2_loadbalancer,
                filename="application_subnets.json",
            ),
            all_matches=True,
        )

    def _subnets(self, instance: dict[str, Any]) -> list[Any]:
        subnets = instance.get("Subnets")
        if isinstance(subnets, list):
            return subnets

        mappings = instance.get("SubnetMappings")
        if isinstance(mappings, list):
            return [
                mapping.get("SubnetId") if isinstance(mapping, dict) else None
                for mapping in mappings
            ]

        return []

    def _in_local_zone(self, validator: Validator, subnet: Any) -> bool:
        fn_key, ref = is_function(subnet)
        if fn_key != "Ref" or not isinstance(ref, str):
            return False

        resources = validator.cfn.template.get("Resources", {})
        if not isinstance(resources, dict):
            return False

        resource = resources.get(ref)
        if not isinstance(resource, dict):
            return False
        if resource.get("Type") != "AWS::EC2::Subnet":
            return False

        properties = resource.get("Properties", {})
        if not isinstance(properties, dict):
            return False

        zone = properties.get("AvailabilityZone")
        return isinstance(zone, str) and bool(_LOCAL_ZONE.match(zone))

    def validate(
        self, validator: Validator, keywords: Any, instance: Any, schema: dict[str, Any]
    ) -> ValidationResult:
        if validator.is_type(instance, "object"):
            subnets = self._subnets(instance)
            if subnets and all(
                self._in_local_zone(validator, subnet) for subnet in subnets
            ):
                return

        yield from super().validate(validator, keywords, instance, schema)
