"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.rules.helpers.get_resource_by_name import get_resource_by_name
from cfnlint.rules.helpers.get_value_from_path import get_value_from_path

__all__ = [
    "get_value_from_path",
    "get_resource_by_name",
]
