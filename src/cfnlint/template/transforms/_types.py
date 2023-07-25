"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any, List, Tuple

from cfnlint.match import Match

TransformResult = Tuple[List[Match], Any]
