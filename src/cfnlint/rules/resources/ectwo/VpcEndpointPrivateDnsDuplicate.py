"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from collections import deque
from typing import Any

from cfnlint.context.conditions import Unsatisfiable
from cfnlint.helpers import ensure_list, is_function
from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules.helpers import get_value_from_path
from cfnlint.rules.jsonschema.CfnLintKeyword import CfnLintKeyword


class VpcEndpointPrivateDnsDuplicate(CfnLintKeyword):
    id = "E3064"
    shortdesc = "Validate unique PrivateDnsEnabled per service per VPC"
    description = (
        "Only one Interface VPC Endpoint per service can have "
        "PrivateDnsEnabled set to true in a VPC. A second endpoint "
        "with the same service and PrivateDnsEnabled will fail to create "
        "due to a conflicting DNS domain."
    )
    source_url = (
        "https://docs.aws.amazon.com/vpc/latest/privatelink/manage-dns-names.html"
    )
    tags = ["resources", "ec2", "vpc"]

    def __init__(self) -> None:
        super().__init__(
            keywords=[
                "Resources/AWS::EC2::VPCEndpoint/Properties",
            ],
        )
        self._endpoints: dict[
            tuple[str, str], list[tuple[list[str | int], dict[str, bool]]]
        ] = {}

    def initialize(self, cfn):
        self._endpoints = {}
        return super().initialize(cfn)

    @staticmethod
    def _resolve_key(value: Any) -> str | None:
        if isinstance(value, str):
            return value
        if not isinstance(value, dict):
            return None
        fn_k, fn_v = is_function(value)
        if fn_k == "Ref":
            return f"Ref:{fn_v}"
        if fn_k == "Fn::GetAtt":
            parts = ensure_list(fn_v)
            return f"GetAtt:{parts[0]}"
        if fn_k == "Fn::Sub":
            if isinstance(fn_v, str):
                return f"Sub:{fn_v}"
            if isinstance(fn_v, list) and fn_v:
                return f"Sub:{fn_v[0]}"
        return None

    def validate(
        self,
        validator: Validator,
        keywords: Any,
        instance: Any,
        schema: dict[str, Any],
    ) -> ValidationResult:
        for endpoint_type, type_validator in get_value_from_path(
            validator, instance, deque(["VpcEndpointType"])
        ):
            if endpoint_type != "Interface":
                continue

            for private_dns, dns_validator in get_value_from_path(
                type_validator, instance, deque(["PrivateDnsEnabled"])
            ):
                if private_dns is not True:
                    continue

                for vpc_id, vpc_validator in get_value_from_path(
                    dns_validator, instance, deque(["VpcId"])
                ):
                    vpc_key = self._resolve_key(vpc_id)
                    if vpc_key is None:
                        continue

                    for service_name, svc_validator in get_value_from_path(
                        vpc_validator, instance, deque(["ServiceName"])
                    ):
                        svc_key = self._resolve_key(service_name)
                        if svc_key is None:
                            continue

                        group_key = (vpc_key, svc_key)
                        if group_key not in self._endpoints:
                            self._endpoints[group_key] = []

                        conditions = svc_validator.context.conditions.status

                        for _, saved_conditions in self._endpoints[group_key]:
                            try:
                                svc_validator.evolve(
                                    context=svc_validator.context.evolve(
                                        conditions=svc_validator.context.conditions.evolve(
                                            saved_conditions
                                        )
                                    )
                                )
                            except Unsatisfiable:
                                continue

                            yield ValidationError(
                                "Only one Interface VPC Endpoint per service "
                                "can have 'PrivateDnsEnabled' set to true in "
                                "a VPC. A second endpoint will fail to create "
                                "due to a conflicting private DNS domain.",
                                rule=self,
                            )

                        self._endpoints[group_key].append(
                            (
                                list(svc_validator.context.path.path),
                                conditions,
                            )
                        )
