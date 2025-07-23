#!/usr/bin/env python
"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
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
from _manual_patches import patches
from _types import AllPatches, ResourcePatches

LOGGER = logging.getLogger("cfnlint")

BOTO_URL = "https://github.com/boto/botocore/archive/refs/heads/master.zip"
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

    LOGGER.setLevel(logging.WARNING)
    log_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    ch.setFormatter(log_formatter)

    # make sure all other log handlers are removed before adding it back
    for handler in LOGGER.handlers:
        LOGGER.removeHandler(handler)
    LOGGER.addHandler(ch)


def build_resource_type_patches(
    boto_path: Path,
    schema_path: Path,
    resource_name: str,
    resource_patches: ResourcePatches,
):
    LOGGER.info(f"Applying patches for {resource_name}")

    resolver = load_schema_file(
        schema_path / f"{resource_name.lower().replace('::', '-')}.json"
    )
    resource_name = resource_name.lower().replace("::", "_")
    output_path = Path("src/cfnlint/data/schemas/patches/extensions/all/")
    resource_path = output_path / resource_name
    if not resource_path.exists():
        resource_path.mkdir(parents=True)
        (resource_path / "__init__.py").touch()

    output_file = resource_path / "boto.json"

    d = []
    boto_d = {}
    for path, patch in resource_patches.items():
        service_path = (
            ["botocore-master/botocore/data"] + patch.source + ["service-2.json"]
        )
        _, schema_data = resolver.resolve(f"#{path}")
        with open(os.path.join(boto_path, *service_path), "r") as f:
            boto_d = json.load(f)
            shape_type = boto_d.get("shapes", {}).get(patch.shape, {}).get("type")
            for field in ["enum", "pattern", "max", "min"]:
                value = boto_d.get("shapes", {}).get(patch.shape, {}).get(field)
                if not value:
                    continue
                if field in ["enum", "pattern"]:
                    if any(f in schema_data for f in ["enum", "pattern"]):
                        continue
                elif field == "max":
                    if any(
                        f in schema_data for f in ["maxLength", "maxItems", "maximum"]
                    ):
                        continue
                    if "pattern" in schema_data:
                        if re.match(
                            r"^.*\{[0-9]+,[0-9]+\}\$?$", schema_data["pattern"]
                        ):
                            continue

                elif field == "min":
                    if any(
                        f in schema_data for f in ["minLength", "minItems", "minimum"]
                    ):
                        continue
                    if "pattern" in schema_data:
                        if re.match(
                            r"^.*\{[0-9]+,[0-9]+\}\$?$", schema_data["pattern"]
                        ):
                            continue
                if field == "pattern":
                    if value in [".*", "^.*$"]:
                        continue
                    try:
                        re.compile(value)
                    except Exception:
                        LOGGER.info(
                            (
                                f"Pattern {value!r} failed to "
                                "compile for resource "
                                f"{resource_name!r}"
                            )
                        )
                        continue
                if field in ["max", "min"]:
                    if shape_type == "string":
                        field = "maxLength" if field == "max" else "minLength"
                    elif shape_type == "list":
                        field = "maxItems" if field == "max" else "minItems"
                    elif shape_type in ["integer", "number"]:
                        field = "maximum" if field == "max" else "minimum"
                    else:
                        continue
                if value:
                    if patch.source[0] in exceptions:
                        if path in exceptions[patch.source[0]]:
                            continue
                    if patch.source[0] in case_insensitive_services and field == "enum":
                        field = "enumCaseInsensitive"
                        value = [v.lower() for v in value]
                    d.append(
                        {
                            "op": "add",
                            "path": f"{path}/{field}",
                            "value": (
                                sorted(value) if isinstance(value, list) else value
                            ),
                        }
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
    boto_path: Path,
    schema_path: Path,
    patches: AllPatches,
):
    for resource_name, patch in patches.items():
        build_resource_type_patches(
            boto_path, schema_path, resource_name=resource_name, resource_patches=patch
        )


def main():
    configure_logging()
    with tempfile.TemporaryDirectory() as dir:
        path = Path(dir)
        boto_path = path / "botocore"
        schema_path = path / "schemas"
        r = requests.get(BOTO_URL)
        z = zipfile.ZipFile(io.BytesIO(r.content))
        z.extractall(boto_path)

        r = requests.get(SCHEMA_URL)
        z = zipfile.ZipFile(io.BytesIO(r.content))
        z.extractall(schema_path)

        _patches = patches
        for k, v in patches.items():
            _patches[k] = v
        for k, v in build_automated_patches(boto_path, schema_path).items():
            if k not in _patches:
                _patches[k] = v
            else:
                for path, patch in v.items():
                    if path in _patches[k]:
                        LOGGER.info(f"Patch {path!r} already found in resource {k!r}")
                    else:
                        _patches[k][path] = patch

        build_patches(boto_path, schema_path, _patches)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, TypeError) as e:
        print(e)
        LOGGER.error(ValueError)
