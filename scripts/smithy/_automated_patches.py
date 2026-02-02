"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0

Extract patches from AWS Smithy API models
"""

import json
import logging
from pathlib import Path
from typing import Any

from _helpers import load_schema_file
from _types import AllPatches, Patch, ResourcePatches

from cfnlint.schema.resolver import RefResolutionError, RefResolver

LOGGER = logging.getLogger("cfnlint")

skip = [
    "account",
    "chime",
    "chime-sdk-identity",
    "chime-sdk-messaging",
    "chime-sdk-meetings",
    "chime-sdk-voice",
    "payment-cryptography-data",
    "rds-data",
    "finspace-data",
    "appconfigdata",
    "iot-jobs-data-plane",
    "dataexchange",
    "bedrock-runtime",
    "swf",
    "cloudhsm",
    "cloudhsm-v2",
    "workdocs",
]

skip_resource_types = ["AWS::CloudFormation::Stack"]
skip_property_names = ["State"]
_visited_paths = []


def renamer(name):
    """Map Smithy service names to CloudFormation service names"""
    manual_fixes = {
        # Special service name mappings
        "acm": "CertificateManager",
        "mq": "AmazonMQ",
        "kafka": "MSK",
        "firehose": "KinesisFirehose",
        "elasticsearch-service": "ElasticSearch",
        "elastic-load-balancing-v2": "ElasticLoadBalancingV2",
        "elastic-load-balancing": "ElasticLoadBalancing",
        "directory-service": "DirectoryService",
        # Hyphenated service names
        "api-gateway": "apigateway",
        "auto-scaling": "autoscaling",
        "auto-scaling-plans": "autoscalingplans",
        "config-service": "config",
        "cost-explorer": "costexplorer",
        "cognito-identity-provider": "cognitoidentityprovider",
        "cognito-identity": "cognitoidentity",
        "application-auto-scaling": "applicationautoscaling",
        "cloudwatch-events": "events",
        "cloudwatch-logs": "logs",
        "database-migration-service": "databasemigrationservice",
        "docdb-elastic": "docdbelastic",
        "resource-explorer-2": "resourceexplorer2",
        "route-53": "route53",
        "sfn": "stepfunctions",
        "ssm-quicksetup": "ssmquicksetup",
        "vpc-lattice": "vpclattice",
        "waf-regional": "wafregional",
    }
    if name in manual_fixes:
        return manual_fixes[name].lower()

    return name.replace("-", "").lower()


def extract_smithy_enum(shape_data: dict[str, Any]) -> list[str] | None:
    """Extract enum values from Smithy enum shape"""
    if shape_data.get("type") != "enum":
        return None

    members = shape_data.get("members", {})
    enum_values = []

    for member_name, member_data in members.items():
        traits = member_data.get("traits", {})
        enum_value = traits.get("smithy.api#enumValue")
        if enum_value:
            enum_values.append(enum_value)

    return sorted(enum_values) if enum_values else None


def extract_smithy_constraints(shape_data: dict[str, Any]) -> dict[str, Any]:
    """Extract min/max/pattern constraints from Smithy traits"""
    constraints = {}
    traits = shape_data.get("traits", {})

    # Length constraint (for strings and lists)
    if "smithy.api#length" in traits:
        length = traits["smithy.api#length"]
        if "min" in length:
            constraints["min"] = length["min"]
        if "max" in length:
            constraints["max"] = length["max"]

    # Range constraint (for numbers)
    if "smithy.api#range" in traits:
        range_data = traits["smithy.api#range"]
        if "min" in range_data:
            constraints["min"] = range_data["min"]
        if "max" in range_data:
            constraints["max"] = range_data["max"]

    # Pattern constraint
    if "smithy.api#pattern" in traits:
        constraints["pattern"] = traits["smithy.api#pattern"]

    return constraints


def get_smithy_shape_by_target(
    smithy_data: dict[str, Any], target: str
) -> dict[str, Any] | None:
    """Resolve a shape by its target reference"""
    result = smithy_data.get("shapes", {}).get(target)
    return result if result is not None else None


def get_shapes(
    smithy_data: dict[str, Any], operation_name: str
) -> dict[str, dict[str, Any]]:
    """Get all shapes with enums/constraints for a given operation"""
    shapes = {}

    for shape_name, shape_data in smithy_data.get("shapes", {}).items():
        result = {}

        # Check for enum
        enum_values = extract_smithy_enum(shape_data)
        if enum_values:
            result["enum"] = enum_values

        # Check for constraints
        constraints = extract_smithy_constraints(shape_data)
        if constraints:
            result.update(constraints)

        if result:
            shapes[shape_name] = result

    return shapes


def get_schema_create_operations(schema_data: dict[str, Any]) -> list[str]:
    """Extract create operation names from CloudFormation schema"""
    results = []
    action_prefixes = ["Put", "Add", "Create", "Register", "Allocate", "Start", "Run"]

    for api in schema_data.get("handlers", {}).get("create", {}).get("permissions", []):
        if ":" not in api:
            continue
        api = api.split(":")[1]
        for action_prefix in action_prefixes:
            if api.startswith(action_prefix):
                results.append(api)

    return results


def find_smithy_operation_input(
    smithy_data: dict[str, Any], operation_name: str
) -> str | None:
    """Find the input shape for a Smithy operation"""
    for shape_name, shape_data in smithy_data.get("shapes", {}).items():
        # Check if this is an operation shape
        if shape_data.get("type") == "operation":
            # Extract operation name from shape name
            # (e.g., "com.amazonaws.ec2#RunInstances")
            if shape_name.endswith(f"#{operation_name}"):
                input_ref = shape_data.get("input", {}).get("target")
                if input_ref is not None:
                    return str(input_ref)

    return None


def _nested_arrays(
    resolver: RefResolver,
    schema_data: dict[str, Any],
    smithy_data: dict[str, Any],
    shape_data: dict[str, Any],
    start_path: str,
    source: list[str],
    shape_name: str,
) -> dict[str, Patch]:
    """Handle nested array structures"""
    # In Smithy, list members are defined with 'member' -> 'target'
    member_target = shape_data.get("member", {}).get("target")
    if not member_target:
        return {}

    array_shape_data = get_smithy_shape_by_target(smithy_data, member_target)
    if not array_shape_data:
        return {}

    path = f"{start_path}/items"
    schema_data = schema_data.get("items", {})
    while "$ref" in schema_data:
        path = schema_data["$ref"][1:]
        schema_data = resolver.resolve_from_url(schema_data["$ref"])

    if array_shape_data.get("type") == "structure":
        return _nested_objects(
            resolver,
            schema_data,
            smithy_data,
            array_shape_data,
            path,
            source,
            member_target,
        )
    else:
        return {
            path: Patch(
                source=source,
                shape=member_target,
            )
        }


def _nested_objects(
    resolver: RefResolver,
    schema_data: dict[str, Any],
    smithy_data: dict[str, Any],
    shape_data: dict[str, Any],
    start_path: str,
    source: list[str],
    shape_name: str,
) -> dict[str, Patch]:
    """Handle nested object structures"""
    results: dict[str, Patch] = {}

    # In Smithy, structure members are in 'members' dict
    for member_name, member_data in shape_data.get("members", {}).items():
        for p_name, p_data in schema_data.get("properties", {}).items():
            if p_name in skip_property_names:
                continue
            if p_name.lower() == member_name.lower():
                path = f"{start_path}/properties/{p_name}"

                global _visited_paths
                if path in _visited_paths:
                    continue

                _visited_paths.append(path)

                while "$ref" in p_data:
                    path = p_data["$ref"][1:]
                    try:
                        p_data = resolver.resolve_from_url(p_data["$ref"])
                    except RefResolutionError:
                        return results

                member_target = member_data.get("target")
                member_shape = get_smithy_shape_by_target(smithy_data, member_target)

                if not member_shape:
                    continue

                if member_shape.get("type") == "structure":
                    if p_data.get("type") == "object":
                        results.update(
                            _nested_objects(
                                resolver,
                                p_data,
                                smithy_data,
                                member_shape,
                                path,
                                source,
                                member_target,
                            )
                        )
                elif member_shape.get("type") == "list":
                    if p_data.get("type") == "array":
                        results.update(
                            _nested_arrays(
                                resolver,
                                p_data,
                                smithy_data,
                                member_shape,
                                path,
                                source,
                                member_target,
                            )
                        )

                results[path] = Patch(
                    source=source,
                    shape=member_target,
                )

    return results


def _per_resource_patch(
    resolver: RefResolver, smithy_data: dict[str, Any], source: list[str]
) -> ResourcePatches:
    """Extract patches for a single resource type"""
    results: ResourcePatches = {}
    _, schema_data = resolver.resolve("/")
    create_operations = get_schema_create_operations(schema_data)
    shapes = {}

    for create_operation in create_operations:
        shapes.update(get_shapes(smithy_data, create_operation))

        input_shape_name = find_smithy_operation_input(smithy_data, create_operation)
        if not input_shape_name:
            continue

        input_shape = get_smithy_shape_by_target(smithy_data, input_shape_name)
        if not input_shape:
            continue

        global _visited_paths
        _visited_paths = []
        results.update(
            _nested_objects(
                resolver,
                schema_data,
                smithy_data,
                input_shape,
                "",
                source,
                input_shape_name,
            )
        )

    return results


def get_latest_version(service_dir: Path) -> str | None:
    """Get the latest version directory for a service"""
    service_path = service_dir / "service"
    if not service_path.exists():
        return None

    versions = []
    for version_dir in service_path.iterdir():
        if version_dir.is_dir():
            versions.append(version_dir.name)

    return max(versions) if versions else None


def get_resource_patches(
    service_dir: Path, schema_path: Path, service_name: str
) -> AllPatches:
    """Extract patches for all resources in a service"""
    results: AllPatches = {}

    # Find latest version
    latest_version = get_latest_version(service_dir)
    if not latest_version:
        return results

    # Load Smithy model
    smithy_file = (
        service_dir
        / "service"
        / latest_version
        / f"{service_dir.name}-{latest_version}.json"
    )
    if not smithy_file.exists():
        LOGGER.warning(f"Smithy model not found: {smithy_file}")
        return results

    smithy_data = {}
    with open(smithy_file, "r") as f:
        smithy_data = json.load(f)

    if not smithy_data:
        return results

    # Find matching CloudFormation resources
    resources = list(schema_path.glob(f"aws-{service_name}-*.json"))
    if not resources:
        LOGGER.debug(f"No resource files found for {service_name}")
        return results

    for resource in resources:
        ref_resolver = load_schema_file(resource)
        _, schema_data = ref_resolver.resolve("/")

        resource_type = schema_data.get("typeName", "")
        if resource_type in skip_resource_types:
            continue
        if resource_type not in results:
            results[resource_type] = {}

        results[resource_type].update(
            _per_resource_patch(
                ref_resolver, smithy_data, [service_dir.name, latest_version]
            )
        )

    return results


def each_smithy_service(smithy_path: Path, schema_path: Path) -> AllPatches:
    """Process all Smithy services"""
    results: AllPatches = {}

    for service_dir in smithy_path.iterdir():
        if not service_dir.is_dir():
            continue

        service_name = renamer(service_dir.name)

        if service_dir.name in skip:
            continue

        LOGGER.info(f"Processing service: {service_dir.name} -> {service_name}")

        _results = get_resource_patches(service_dir, schema_path, service_name)
        for type_name, patches in _results.items():
            if patches:
                results[type_name] = patches

    return results


def build_automated_patches(smithy_path: Path, schema_path: Path) -> AllPatches:
    """Main entry point for building patches from Smithy models"""
    # The zip extracts to api-models-aws-main/models
    models_path = smithy_path / "api-models-aws-main" / "models"
    if not models_path.exists():
        raise ValueError(f"Smithy models path not found: {models_path}")

    return each_smithy_service(models_path, schema_path)
