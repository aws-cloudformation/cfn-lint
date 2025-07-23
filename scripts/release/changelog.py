#!/usr/bin/env python
"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import argparse
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--version")
args = parser.parse_args()

with open("CHANGELOG.md", "r") as f:
    text = f.read()

output = []

for line in text.splitlines():
    if line.startswith("### "):
        if args.version == line[3:].strip():
            found = True
        elif found:
            break
    else:
        if found:
            output.append(line)

build_dir = Path("build")
with open(build_dir / "CHANGELOG.md", "w") as f:
    f.write("\n".join(output))
