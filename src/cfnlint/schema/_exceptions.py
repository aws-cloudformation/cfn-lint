"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations


class ResourceNotFoundError(Exception):
    def __init__(self, resource_type: str, region: str):
        super().__init__(f"Resource type '{resource_type}' is not found in '{region}'")


class SchemaNotFoundError(Exception):
    def __init__(self, path: str):
        super().__init__(f"Schema '{path}' is not found")
