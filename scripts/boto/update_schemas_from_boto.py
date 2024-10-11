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

import requests
from _manual_patches import patches
from _types import ResourcePatches

LOGGER = logging.getLogger("cfnlint")

BOTO_URL = "https://github.com/boto/botocore/archive/refs/heads/master.zip"


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


def build_resource_type_patches(
    dir: str, resource_name: str, resource_patches: ResourcePatches
):
    LOGGER.info(f"Applying patches for {resource_name}")

    resource_name = resource_name.lower().replace("::", "_")
    output_dir = os.path.join("src/cfnlint/data/schemas/patches/extensions/all/")
    output_file = os.path.join(
        output_dir,
        resource_name,
        "boto.json",
    )

    with open(output_file, "w+") as fh:
        d = []
        boto_d = {}
        for path, patch in resource_patches.items():
            enums = []
            print(patch.source)
            service_path = (
                ["botocore-master/botocore/data"] + patch.source + ["service-2.json"]
            )
            with open(os.path.join(dir, *service_path), "r") as f:
                boto_d = json.load(f)

                try:
                    enums = boto_d.get("shapes").get(patch.shape).get("enum")  # type: ignore
                    d.append(
                        {
                            "op": "add",
                            "path": f"{path}/enum",
                            "value": sorted(enums),
                        }
                    )
                except AttributeError as e:
                    print(f"{patch.source}, {patch.shape}")
                    print(e)

        json.dump(
            d,
            fh,
            indent=1,
            separators=(",", ": "),
            sort_keys=True,
        )
        fh.write("\n")


def build_patches(dir: str):
    for resource_name, patch in patches.items():
        build_resource_type_patches(
            dir, resource_name=resource_name, resource_patches=patch
        )


def main():
    """main function"""
    configure_logging()
    with tempfile.TemporaryDirectory() as dir:
        r = requests.get(BOTO_URL)
        z = zipfile.ZipFile(io.BytesIO(r.content))
        z.extractall(dir)

        build_patches(dir)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, TypeError) as e:
        print(e)
        LOGGER.error(ValueError)
