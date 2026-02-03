#!/usr/bin/env python
"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0

Update CloudFormation schemas with patches from AWS Smithy API models
"""

import io
import json
import logging
import os
import tempfile
import zipfile
from pathlib import Path

import regex as re
import requests
from _automated_patches import build_automated_patches
from _helpers import load_schema_file
from _types import AllPatches, ResourcePatches

LOGGER = logging.getLogger("cfnlint")

SMITHY_URL = "https://github.com/aws/api-models-aws/archive/refs/heads/main.zip"
SCHEMA_URL = (
    "https://schema.cloudformation.us-east-1.amazonaws.com/CloudformationSchema.zip"
)

case_insensitive_services = [
    "batch",
]

exceptions = {
    "ses": ["/definitions/EventDestination/properties/MatchingEventTypes/items"],
    "ecs": ["/definitions/LogConfiguration/properties/LogDriver"],
}


def configure_logging():
    """Setup Logging"""
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    LOGGER.setLevel(logging.INFO)
    log_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    ch.setFormatter(log_formatter)

    # make sure all other log handlers are removed before adding it back
    for handler in LOGGER.handlers:
        LOGGER.removeHandler(handler)
    LOGGER.addHandler(ch)


def extract_smithy_enum(shape_data: dict) -> list[str] | None:
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


def extract_smithy_constraints(shape_data: dict) -> dict:
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


def build_resource_type_patches(
    smithy_path: Path,
    schema_path: Path,
    resource_name: str,
    resource_patches: ResourcePatches,
):
    LOGGER.info(f"Applying patches for {resource_name}")

    resolver = load_schema_file(
        schema_path / f"{resource_name.lower().replace('::', '-')}.json"
    )
    resource_name_path = resource_name.lower().replace("::", "_")
    output_path = Path("src/cfnlint/data/schemas/patches/extensions/all/")
    resource_path = output_path / resource_name_path
    if not resource_path.exists():
        resource_path.mkdir(parents=True)
        (resource_path / "__init__.py").touch()

    output_file = resource_path / "smithy.json"

    d = []
    smithy_d = {}

    for path, patch in resource_patches.items():
        # Build path to Smithy model file
        # patch.source is [service_name, version]
        service_path = [
            "api-models-aws-main/models",
            patch.source[0],
            "service",
            patch.source[1],
            f"{patch.source[0]}-{patch.source[1]}.json",
        ]

        _, schema_data = resolver.resolve(f"#{path}")

        smithy_file = os.path.join(smithy_path, *service_path)
        if not os.path.exists(smithy_file):
            LOGGER.warning(f"Smithy file not found: {smithy_file}")
            continue

        with open(smithy_file, "r") as f:
            smithy_d = json.load(f)

            # Get the shape data
            shape_data = smithy_d.get("shapes", {}).get(patch.shape, {})
            if not shape_data:
                continue

            shape_type = shape_data.get("type")

            # Extract enum values
            enum_values = extract_smithy_enum(shape_data)
            if enum_values:
                if any(
                    f in schema_data for f in ["enum", "pattern", "properties", "items"]
                ):
                    continue

                # Check for case insensitive services
                field = "enum"
                value = enum_values
                if patch.source[0] in case_insensitive_services:
                    field = "enumCaseInsensitive"
                    value = [v.lower() for v in value]

                if patch.source[0] in exceptions:
                    if path in exceptions[patch.source[0]]:
                        continue

                d.append(
                    {"op": "add", "path": f"{path}/{field}", "value": sorted(value)}
                )
                continue

            # Extract constraints
            constraints = extract_smithy_constraints(shape_data)

            for field, value in constraints.items():
                if field == "pattern":
                    if any(
                        f in schema_data
                        for f in ["enum", "pattern", "properties", "items"]
                    ):
                        continue
                    if value in [".*", "^.*$"]:
                        continue
                    if isinstance(value, str):
                        try:
                            re.compile(value)
                        except Exception:
                            LOGGER.info(
                                f"Pattern {value!r} failed to compile "
                                f"for resource {resource_name!r}"
                            )
                            continue

                    d.append({"op": "add", "path": f"{path}/{field}", "value": value})

                elif field in ["max", "min"]:
                    # Determine the correct JSON Schema field based on shape type
                    if shape_type == "string":
                        json_field = "maxLength" if field == "max" else "minLength"
                    elif shape_type == "list":
                        json_field = "maxItems" if field == "max" else "minItems"
                    elif shape_type in ["integer", "long", "float", "double"]:
                        json_field = "maximum" if field == "max" else "minimum"
                    else:
                        continue

                    if any(f in schema_data for f in [json_field]):
                        continue
                    if "pattern" in schema_data:
                        if re.match(
                            r"^.*\{[0-9]+,[0-9]+\}\$?$", schema_data["pattern"]
                        ):
                            continue

                    if patch.source[0] in exceptions:
                        if path in exceptions[patch.source[0]]:
                            continue

                    d.append(
                        {"op": "add", "path": f"{path}/{json_field}", "value": value}
                    )

    if not d:
        return

    with open(output_file, "w+") as fh:
        json.dump(
            d,
            fh,
            indent=1,
            separators=(",", ": "),
            sort_keys=True,
        )
        fh.write("\n")


def build_patches(
    smithy_path: Path,
    schema_path: Path,
    patches: AllPatches,
):
    for resource_name, patch in patches.items():
        build_resource_type_patches(
            smithy_path,
            schema_path,
            resource_name=resource_name,
            resource_patches=patch,
        )


def main():
    configure_logging()
    with tempfile.TemporaryDirectory() as dir:
        path = Path(dir)
        smithy_path = path / "smithy"
        schema_path = path / "schemas"

        LOGGER.info("Downloading Smithy API models...")
        r = requests.get(SMITHY_URL)
        z = zipfile.ZipFile(io.BytesIO(r.content))
        z.extractall(smithy_path)

        LOGGER.info("Downloading CloudFormation schemas...")
        r = requests.get(SCHEMA_URL)
        z = zipfile.ZipFile(io.BytesIO(r.content))
        z.extractall(schema_path)

        LOGGER.info("Building automated patches from Smithy models...")
        _patches = build_automated_patches(smithy_path, schema_path)

        LOGGER.info(f"Found patches for {len(_patches)} resource types")
        build_patches(smithy_path, schema_path, _patches)

        LOGGER.info("Done!")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, TypeError) as e:
        LOGGER.error(f"Error: {e}")
        raise
