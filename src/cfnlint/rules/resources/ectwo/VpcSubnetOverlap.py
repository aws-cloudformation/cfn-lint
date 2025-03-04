"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import logging
from collections import deque
from ipaddress import IPv4Network, IPv6Network, ip_network
from typing import Any

from cfnlint.context.conditions import Unsatisfiable
from cfnlint.helpers import ensure_list, is_function
from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules.helpers import get_value_from_path
from cfnlint.rules.jsonschema.CfnLintKeyword import CfnLintKeyword

LOGGER = logging.getLogger(__name__)


class VpcSubnetOverlap(CfnLintKeyword):
    id = "E3060"
    shortdesc = "Validate subnet CIDRs do not overlap with other subnets"
    description = (
        "When specifying subnet CIDRs for a VPC the subnet CIDRs "
        "most not overlap with eachother"
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnet.html"
    tags = ["resources", "ec2", "vpc", "subnet"]

    def __init__(self) -> None:
        super().__init__(
            keywords=[
                "Resources/AWS::EC2::Subnet/Properties",
            ],
        )
        self._subnets: dict[str, list[tuple[IPv4Network | IPv6Network, dict]]] = {}

    def initialize(self, cfn):
        self._subnets = {}
        return super().initialize(cfn)

    def _validate_subnets(
        self,
        source: IPv4Network | IPv6Network,
        destination: IPv4Network | IPv6Network,
    ) -> bool:
        if isinstance(source, IPv4Network) and isinstance(destination, IPv4Network):
            if source.overlaps(destination):
                return True
            return False
        elif isinstance(source, IPv6Network) and isinstance(destination, IPv6Network):
            if source.overlaps(destination):
                return True
            return False
        return False

    def _create_network(self, cidr: Any) -> IPv4Network | IPv6Network | None:
        if not isinstance(cidr, str):
            return None

        try:
            return ip_network(cidr)
        except Exception as e:
            LOGGER.debug(f"Unable to create network from {cidr}", e)

        return None

    def validate(
        self, validator: Validator, keywords: Any, instance: Any, schema: dict[str, Any]
    ) -> ValidationResult:

        for vpc_id, vpc_validator in get_value_from_path(
            validator=validator, instance=instance, path=deque(["VpcId"])
        ):

            if not isinstance(vpc_id, (str, dict)):
                return

            fn_k, fn_v = is_function(vpc_id)
            if fn_k == "Fn::GetAtt":
                vpc_id = ensure_list(fn_v)[0].split(".")[0]
            elif fn_k == "Ref":
                vpc_id = fn_v
            elif fn_k:
                # its a function that we can't resolve
                return

            if not validator.is_type(vpc_id, "string"):
                return
            if vpc_id not in self._subnets:
                self._subnets[vpc_id] = []

            for key in ["CidrBlock", "Ipv6CidrBlock"]:
                for cidr_block, cidr_block_validator in get_value_from_path(
                    validator=vpc_validator, instance=instance, path=deque([key])
                ):

                    cidr_network = self._create_network(cidr_block)
                    if not cidr_network:
                        continue

                    for saved_subnet, conditions in self._subnets[vpc_id]:
                        # attempt to validate if the saved conditions comply
                        # with these conditions
                        try:
                            cidr_block_validator.evolve(
                                context=cidr_block_validator.context.evolve(
                                    conditions=cidr_block_validator.context.conditions.evolve(
                                        conditions
                                    )
                                )
                            )
                        except Unsatisfiable:
                            continue

                        # now we can evaluate if they overlap
                        if self._validate_subnets(
                            cidr_network,
                            saved_subnet,
                        ):
                            yield ValidationError(
                                (
                                    f"{str(cidr_network)!r} overlaps "
                                    f"with {str(saved_subnet)!r}"
                                ),
                                rule=self,
                                path=deque(
                                    list(cidr_block_validator.context.path.path)[1:]
                                ),
                            )

                    self._subnets[vpc_id].append(
                        (cidr_network, cidr_block_validator.context.conditions.status)
                    )
