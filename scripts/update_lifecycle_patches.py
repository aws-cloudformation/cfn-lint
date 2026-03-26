#!/usr/bin/env python
"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0

Generate lifecycle patches for deprecated/sunset/shutdown resource types.

Sources:
- https://docs.aws.amazon.com/general/latest/gr/full_shutdown_services.html
- https://docs.aws.amazon.com/general/latest/gr/sunset_services.html
- https://docs.aws.amazon.com/general/latest/gr/maintenance_services.html
"""

import glob
import json
import logging
import os

LOGGER = logging.getLogger("cfnlint")

# (prefix, date)
SHUTDOWN = [
    ("AWS::CodeStar::GitHubRepository", "2024-07-25"),
    ("AWS::Evidently", "2025-10-17"),
    ("AWS::IoTAnalytics", "2025-12-15"),
    ("AWS::IoTEvents", "2026-05-20"),
    ("AWS::IoTThingsGraph", "2022-11-09"),
    ("AWS::NimbleStudio", "2024-06-30"),
    ("AWS::OpsWorks", "2024-05-01"),
    ("AWS::QLDB", "2025-07-31"),
]

SUNSET = [
    ("AWS::AppMesh", "2026-09-30"),
    ("AWS::FinSpace", "2026-10-07"),
    ("AWS::FraudDetector", "2025-11-07"),
    ("AWS::Greengrass::", "2026-10-01"),
    ("AWS::Inspector::", "2026-05-20"),
    ("AWS::MediaStore", "2025-11-13"),
    ("AWS::Pinpoint", "2026-10-30"),
    ("AWS::Proton", "2026-10-07"),
    ("AWS::SimSpaceWeaver", "2026-05-20"),
    ("AWS::WAF::", ""),
    ("AWS::WAFRegional", ""),
]

MAINTENANCE = [
    ("AWS::Cloud9", "2024-07-25"),
    ("AWS::CodeGuruReviewer", "2025-10-07"),
    ("AWS::Forecast", "2024-07-29"),
    ("AWS::Timestream", "2025-06-20"),
    ("AWS::AutoScaling::LaunchConfiguration", "2024-10-01"),
]


def get_resource_types(schema_dir):
    types = {}
    for f in glob.glob(os.path.join(schema_dir, "*.json")):
        with open(f) as fh:
            schema = json.load(fh)
            tn = schema.get("typeName", "")
            if tn:
                types[tn] = f
    return types


def _match_types(all_types, prefix):
    return [
        tn
        for tn in all_types
        if tn.startswith(prefix)
        and (prefix.endswith("::") or tn == prefix or tn[len(prefix)] == ":")
    ]


def _write_patch(patches_dir, type_name, status, date):
    dir_name = type_name.lower().replace("::", "_")
    output_dir = os.path.join(patches_dir, dir_name)
    output_file = os.path.join(output_dir, "lifecycle.json")

    os.makedirs(output_dir, exist_ok=True)
    init_file = os.path.join(output_dir, "__init__.py")
    if not os.path.exists(init_file):
        with open(init_file, "w"):
            pass

    value = {"status": status}
    if date:
        value["date"] = date

    patch = [{"op": "add", "path": "/lifecycle", "value": value}]

    with open(output_file, "w") as fh:
        json.dump(patch, fh, indent=1, separators=(",", ": "), sort_keys=True)
        fh.write("\n")

    LOGGER.info("  %s -> %s (%s)", type_name, status, date or "no date")
    return 1


def main():
    logging.basicConfig(level=logging.INFO)

    schema_dir = os.path.join(
        os.path.dirname(__file__),
        "..",
        "src",
        "cfnlint",
        "data",
        "schemas",
        "resources",
    )
    patches_dir = os.path.join(
        os.path.dirname(__file__),
        "..",
        "src",
        "cfnlint",
        "data",
        "schemas",
        "patches",
        "extensions",
        "all",
    )

    all_types = get_resource_types(schema_dir)
    count = 0

    for status, services in [
        ("shutdown", SHUTDOWN),
        ("sunset", SUNSET),
        ("maintenance", MAINTENANCE),
    ]:
        for prefix, date in services:
            for type_name in _match_types(all_types, prefix):
                count += _write_patch(patches_dir, type_name, status, date)

    LOGGER.info("Wrote %d lifecycle patches", count)


if __name__ == "__main__":
    main()
