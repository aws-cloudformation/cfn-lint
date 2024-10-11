"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import namedtuple

Patch = namedtuple("Patch", ["source", "shape"])
ResourcePatches = dict[str, Patch]
AllPatches = dict[str, ResourcePatches]
