"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import json
from pathlib import Path
from typing import Any

from _types import AllPatches, Patch, ResourcePatches

from cfnlint.schema.resolver import RefResolver

skip = [
    "account",
    "chime",
    "chimesdkidentity",
    "chimesdkmessaging",
    "chimesdkmeetings",
    "chimesdkvoice",
    "paymentcryptographydata",
    "rdsdata",
    "finspacedata",
    "appconfigdata",
    "iotjobsdata",
    "dataexchange",
    "bedrockruntime",
    "swf",
    "cloudhsm",
    "cloudhsmv2",
    "workdocs",
]

skip_property_names = ["State"]

_fields = ["pattern", "enum"]

_visited_paths = []


def renamer(name):
    manual_fixes = {
        "acm": "CertificateManager",
        "mq": "AmazonMQ",
        "kafka": "MSK",
        "firehose": "KinesisFirehose",
        "es": "ElasticSearch",
        "elbv2": "ElasticLoadBalancingV2",
        "elb": "ElasticLoadBalancing",
        "ds": "DirectoryService",
    }
    if name in manual_fixes:
        return manual_fixes[name].lower()

    return name.replace("-", "").lower()


def get_shapes(data: dict[str, Any], name: str):
    shapes: dict[str, Any] = {}

    input_shape = data.get("operations", {}).get(name, {}).get("input", {}).get("shape")
    if not input_shape:
        return shapes

    for shape_name, shap_data in data.get("shapes", {}).items():
        if "enum" in shap_data:
            shapes[shape_name] = {"enum": shap_data.get("enum")}

    return shapes


def get_schema_create_operations(data: dict[str, Any]) -> list[str]:
    results = []

    action_prefixes = ["Put", "Add", "Create", "Register", "Allocate", "Start", "Run"]

    for api in data.get("handlers", {}).get("create", {}).get("permissions", []):
        if ":" not in api:
            continue
        api = api.split(":")[1]
        for action_prefix in action_prefixes:
            if api.startswith(action_prefix):
                results.append(api)

    return results


def get_last_date(service_dir: Path) -> str:
    last_date = "0000-00-00"
    for date_dir in service_dir.iterdir():
        if not date_dir.is_dir():
            continue

        if date_dir.name > last_date:
            last_date = date_dir.name

    return last_date


def _nested_arrays(
    resolver: RefResolver,
    schema_data: dict[str, Any],
    boto_data: dict[str, Any],
    shape_data: dict[str, Any],
    start_path: str,
    source: list[str],
):

    shape = shape_data.get("member", {}).get("shape")
    if not shape:
        return []

    array_shap_data = boto_data.get("shapes", {}).get(shape)

    path = f"{start_path}/items"
    schema_data = schema_data.get("items", {})
    while True:
        if "$ref" not in schema_data:
            break
        path = schema_data["$ref"][1:]
        schema_data = resolver.resolve_from_url(schema_data["$ref"])

    if array_shap_data.get("type") == "structure":
        return _nested_objects(
            resolver, schema_data, boto_data, array_shap_data, path, source
        )
    else:
        # skip if we already have an enum or pattern
        if any([schema_data.get(field) for field in _fields]):
            return {}
        return {
            path: Patch(
                source=source,
                shape=shape,
            )
        }


def _nested_objects(
    resolver: RefResolver,
    schema_data: dict[str, Any],
    boto_data: dict[str, Any],
    shape_data: dict[str, Any],
    start_path: str,
    source: list[str],
):
    results = {}
    for member, member_data in shape_data.get("members", {}).items():
        for p_name, p_data in schema_data.get("properties", {}).items():
            if p_name in skip_property_names:
                continue
            if p_name.lower() == member.lower():
                path = f"{start_path}/properties/{p_name}"

                global _visited_paths
                if path in _visited_paths:
                    continue

                _visited_paths.append(path)

                while True:
                    if "$ref" not in p_data:
                        break
                    path = p_data["$ref"][1:]
                    p_data = resolver.resolve_from_url(p_data["$ref"])

                # skip if we already have an enum or pattern
                if any([p_data.get(field) for field in _fields]):
                    continue

                member_shape_name = member_data.get("shape")
                member_shape = boto_data.get("shapes", {}).get(member_shape_name, {})

                if member_shape.get("type") == "structure":
                    if p_data.get("type") == "object":
                        results.update(
                            _nested_objects(
                                resolver, p_data, boto_data, member_shape, path, source
                            )
                        )
                elif member_shape.get("type") == "list":
                    if p_data.get("type") == "array":
                        results.update(
                            _nested_arrays(
                                resolver, p_data, boto_data, member_shape, path, source
                            )
                        )

                if not any([member_shape.get(field) for field in _fields]):
                    continue

                results[path] = Patch(
                    source=source,
                    shape=member_shape_name,
                )

    return results


def _per_resource_patch(
    schema_data: dict[str, Any], boto_data: dict[str, Any], source: list[str]
) -> ResourcePatches:
    results: ResourcePatches = {}
    create_operations = get_schema_create_operations(schema_data)
    shapes = {}

    resolver = RefResolver.from_schema(schema_data)
    for create_operation in create_operations:
        shapes.update(get_shapes(boto_data, create_operation))
        create_shape = (
            boto_data.get("operations", {})
            .get(create_operation, {})
            .get("input", {})
            .get("shape")
        )

        global _visited_paths
        _visited_paths = []
        results.update(
            _nested_objects(
                resolver,
                schema_data,
                boto_data,
                boto_data.get("shapes", {}).get(create_shape, {}),
                "",
                source,
            )
        )

    return results


def get_resource_patches(
    service_dir: Path, schema_path: Path, service_name: str, last_date: str
) -> AllPatches:

    results: AllPatches = {}

    services_file = Path(f"{service_dir}/{last_date}/service-2.json")
    if not services_file.exists():
        return results

    boto_data = {}
    with open(services_file, "r") as f:
        boto_data = json.load(f)

    if not boto_data:
        return results

    resources = list(schema_path.glob(f"aws-{service_name}-*.json"))
    if not resources:
        print(f"No resource files found for {service_name}")

    for resource in resources:
        with open(resource, "r") as f:
            schema_data = json.load(f)

            resource_type = schema_data.get("typeName", "")
            if resource_type not in results:
                results[resource_type] = {}

            results[resource_type].update(
                _per_resource_patch(
                    schema_data, boto_data, [service_dir.name, last_date]
                )
            )

    return results


def each_boto_service(boto_path: Path, schema_path: Path) -> AllPatches:
    results: AllPatches = {}
    _results: AllPatches = {}
    boto_path = boto_path / "botocore-master" / "botocore" / "data"

    for service_dir in boto_path.iterdir():
        if not service_dir.is_dir():
            continue

        service_name = renamer(service_dir.name)

        if service_name in skip:
            continue

        last_date = get_last_date(service_dir)

        _results = get_resource_patches(
            service_dir, schema_path, service_name, last_date
        )
        for type_name, patches in _results.items():
            if patches:
                results[type_name] = patches

    return results


def build_automated_patches(boto_path: Path, schema_path: Path) -> AllPatches:
    return each_boto_service(boto_path, schema_path)
