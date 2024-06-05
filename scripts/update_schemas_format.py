#!/usr/bin/env python
"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import json
import logging
import os
from collections import deque
from typing import Any, Iterator, Sequence

from update_schemas_manually import Patch, ResourcePatch, build_patches

from cfnlint.schema.resolver import RefResolver

LOGGER = logging.getLogger("cfnlint")


def _descend(instance: Any, keywords: Sequence[str]) -> Iterator[deque[str]]:
    if isinstance(instance, dict):
        for k, v in instance.items():
            if k in keywords:
                yield deque([k])
            for e in _descend(v, keywords):
                if e:
                    yield deque([k, *e])
    if isinstance(instance, list):
        for i, v in enumerate(instance):
            for e in _descend(v, keywords):
                if e:
                    yield deque([str(i), *e])

    return


def _create_security_group_ids_patch(type_name: str, ref: str, resolver: RefResolver):
    if type_name in ["AWS::Pipes::Pipe", "AWS::EC2::NetworkInsightsAnalysis"]:
        return []

    _, resolved = resolver.resolve(ref)
    if "$ref" in resolved:
        return _create_security_group_ids_patch(
            type_name=type_name,
            ref=resolved["$ref"],
            resolver=resolver,
        )
    items = resolved.get("items")
    if items:
        if "$ref" in items:
            items_path = items["$ref"]
        else:
            items_path = ref + "/items"

    return [
        Patch(
            values={"format": "AWS::EC2::SecurityGroup.Ids"},
            path=ref[1:],
        ),
        _create_patch(
            {"format": "AWS::EC2::SecurityGroup.GroupId"},
            items_path,
            resolver=resolver,
        ),
    ]


def _create_security_group_id(type_name: str, ref: str, resolver: RefResolver):
    if type_name in ["AWS::Pipes::Pipe", "AWS::EC2::NetworkInsightsAnalysis"]:
        return []

    _, resolved = resolver.resolve(ref)
    if "$ref" in resolved:
        return _create_security_group_id(
            type_name=type_name,
            ref=resolved["$ref"],
            resolver=resolver,
        )

    return [
        _create_patch(
            {"format": "AWS::EC2::SecurityGroup.GroupId"},
            ref,
            resolver=resolver,
        )
    ]


def _create_patch(value: dict[str, str], ref: Sequence[str], resolver: RefResolver):
    _, resolved = resolver.resolve(ref)
    if "$ref" in resolved:
        return _create_patch(value, resolved["$ref"], resolver)

    return Patch(
        values=value,
        path=ref[1:],
    )


_manual_patches = {
    "AWS::EC2::SecurityGroup": [
        Patch(
            values={"format": "AWS::EC2::SecurityGroup.GroupId"},
            path="properties/GroupId",
        ),
    ],
    "AWS::EC2::SecurityGroupIngress": [
        Patch(
            values={"format": "AWS::EC2::SecurityGroup.GroupId"},
            path="properties/GroupId",
        ),
    ],
    "AWS::EC2::SecurityGroupEgress": [
        Patch(
            values={"format": "AWS::EC2::SecurityGroup.GroupId"},
            path="properties/GroupId",
        ),
    ],
    "AWS::EC2::VPC": [
        Patch(
            values={"format": "AWS::EC2::VPC.Id"},
            path="properties/Id",
        ),
    ],
}


def main():
    schema_dir = os.path.join("src/cfnlint/data/schemas/providers/us_east_1")
    patches = []
    for root, dirs, files in os.walk(schema_dir, topdown=False):
        for file in files:
            if file in [".DS_Store"]:
                continue

            if file.startswith("__init__"):
                continue

            obj = json.load(open(os.path.join(root, file)))

            resolver = RefResolver.from_schema(obj)
            resource_type = obj["typeName"]

            resource_patches = []
            if resource_type in _manual_patches:
                resource_patches.extend(_manual_patches[resource_type])

            for path in _descend(obj, ["VpcId", "VPCId"]):
                if path[-2] == "properties":
                    resource_patches.append(
                        _create_patch(
                            value={"format": "AWS::EC2::VPC.Id"},
                            ref="#/" + "/".join(path),
                            resolver=resolver,
                        )
                    )

            for path in _descend(obj, ["ImageId", "AmiId"]):
                if path[-2] == "properties":
                    resource_patches.append(
                        _create_patch(
                            value={"format": "AWS::EC2::Image.Id"},
                            ref="#/" + "/".join(path),
                            resolver=resolver,
                        )
                    )

            for path in _descend(obj, ["SecurityGroupIds", "SecurityGroups"]):
                if path[-2] == "properties":
                    resource_patches.extend(
                        _create_security_group_ids_patch(
                            resource_type, "#/" + "/".join(path), resolver
                        )
                    )

            for path in _descend(
                obj,
                [
                    "DefaultSecurityGroup",
                    "SourceSecurityGroupId",
                    "DestinationSecurityGroupId",
                    "SecurityGroup",
                    "SecurityGroupId",
                ],
            ):
                if path[-2] == "properties":
                    resource_patches.extend(
                        _create_security_group_id(
                            resource_type, "#/" + "/".join(path), resolver
                        )
                    )

            if resource_patches:
                patches.append(
                    ResourcePatch(
                        resource_type=resource_type,
                        patches=resource_patches,
                    )
                )

    build_patches(patches, "format.json")
    # specs = read_specs()


if __name__ == "__main__":
    try:
        main()
    except (ValueError, TypeError) as e:
        print(e)
        LOGGER.error(ValueError)
