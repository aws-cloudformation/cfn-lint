"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import logging
from collections import deque
from ipaddress import IPv4Network, IPv6Network, ip_network
from typing import Any, Iterator

from cfnlint.context import Path
from cfnlint.jsonschema import ValidationError, ValidationResult, Validator
from cfnlint.rules.helpers import get_value_from_path
from cfnlint.rules.jsonschema.CfnLintKeyword import CfnLintKeyword

LOGGER = logging.getLogger(__name__)


class VpcSubnetCidr(CfnLintKeyword):
    id = "E3059"
    shortdesc = "Validate subnet CIDRs are within the CIDRs of the VPC"
    description = (
        "When specifying subnet CIDRs for a VPC the subnet CIDRs "
        "most be within the VPC CIDRs"
    )
    source_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnet.html"
    tags = ["resources", "ec2", "vpc", "subnet"]

    def __init__(self) -> None:
        super().__init__(
            keywords=[
                "Resources/AWS::EC2::VPC/Properties",
            ],
        )

    def _validate_subnets(
        self,
        source: IPv4Network | IPv6Network,
        destination: IPv4Network | IPv6Network,
    ) -> bool:
        if isinstance(source, IPv4Network) and isinstance(destination, IPv4Network):
            if source.subnet_of(destination):
                return True
            return False
        elif isinstance(source, IPv6Network) and isinstance(destination, IPv6Network):
            if source.subnet_of(destination):
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

    def _get_vpc_cidrs(
        self, validator: Validator, instance: dict[str, Any]
    ) -> Iterator[tuple[IPv4Network | IPv6Network | None, Validator]]:
        for key in [
            "Ipv4IpamPoolId",
            "Ipv6IpamPoolId",
            "Ipv6Pool",
            "AmazonProvidedIpv6CidrBlock",
        ]:
            for value, value_validator in get_value_from_path(
                validator,
                instance,
                deque([key]),
            ):
                if value is None:
                    continue
                yield None, value_validator

        for key in ["CidrBlock", "Ipv6CidrBlock"]:
            for cidr, cidr_validator in get_value_from_path(
                validator,
                instance,
                deque([key]),
            ):

                if cidr is None:
                    continue
                yield self._create_network(cidr), cidr_validator

    def validate(
        self, validator: Validator, keywords: Any, instance: Any, schema: dict[str, Any]
    ) -> ValidationResult:

        if not validator.cfn.graph:
            return

        vpc_ipv4_networks: list[IPv4Network] = []
        vpc_ipv6_networks: list[IPv6Network] = []
        for vpc_network, _ in self._get_vpc_cidrs(validator, instance):
            if not vpc_network:
                return
            if isinstance(vpc_network, IPv4Network):
                vpc_ipv4_networks.append(vpc_network)
            # you can't specify IPV6 networks on a VPC

        template_validator = validator.evolve(
            context=validator.context.evolve(path=Path())
        )

        # dynamic vpc network (using IPAM or AWS provided)
        # allows to validate subnet overlapping even if using
        # dynamic networks
        has_dynamic_network = False

        for source, _ in validator.cfn.graph.graph.in_edges(
            validator.context.path.path[1]
        ):
            if (
                validator.cfn.graph.graph.nodes[source].get("resource_type")
                == "AWS::EC2::VPCCidrBlock"
            ):
                for cidr_props, cidr_validator in get_value_from_path(
                    template_validator,
                    validator.cfn.template,
                    deque(["Resources", source, "Properties"]),
                ):
                    for cidr_network, _ in self._get_vpc_cidrs(
                        cidr_validator, cidr_props
                    ):
                        if not cidr_network:
                            has_dynamic_network = True
                            continue
                        if isinstance(cidr_network, IPv4Network):
                            vpc_ipv4_networks.append(cidr_network)
                        else:
                            vpc_ipv6_networks.append(cidr_network)

        subnets: list[tuple[IPv4Network | IPv6Network, deque]] = []
        for source, _ in validator.cfn.graph.graph.in_edges(
            validator.context.path.path[1]
        ):
            if (
                validator.cfn.graph.graph.nodes[source].get("resource_type")
                == "AWS::EC2::Subnet"
            ):
                for subnet_props, source_validator in get_value_from_path(
                    template_validator,
                    validator.cfn.template,
                    deque(["Resources", source, "Properties"]),
                ):
                    for subnet_network, subnet_validator in self._get_vpc_cidrs(
                        source_validator, subnet_props
                    ):
                        if not subnet_network:
                            continue

                        subnets.append(
                            (subnet_network, subnet_validator.context.path.path)
                        )
                        if has_dynamic_network:
                            continue
                        if not any(
                            self._validate_subnets(
                                subnet_network,
                                vpc_network,
                            )
                            for vpc_network in vpc_ipv4_networks + vpc_ipv6_networks
                        ):
                            if isinstance(subnet_network, IPv4Network):
                                # Every VPC has to have a ipv4 network
                                # we continue if there isn't one
                                if not vpc_ipv4_networks:
                                    continue
                                reprs = (
                                    "is not a valid subnet of "
                                    f"{[f'{str(v)}' for v in vpc_ipv4_networks]!r}"
                                )
                            else:
                                if not vpc_ipv6_networks:
                                    reprs = (
                                        "is specified on a VPC that has "
                                        "no ipv6 networks defined"
                                    )
                                else:
                                    reprs = (
                                        "is not a valid subnet of "
                                        f"{[f'{str(v)}' for v in vpc_ipv6_networks]!r}"
                                    )
                            yield ValidationError(
                                (f"{str(subnet_network)!r} {reprs}"),
                                rule=self,
                                path_override=subnet_validator.context.path.path,
                            )
                            continue
