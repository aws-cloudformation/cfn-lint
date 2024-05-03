"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from dataclasses import dataclass


@dataclass
class Mark:
    """Mark of line and column"""

    line: int = 1
    column: int = 1
