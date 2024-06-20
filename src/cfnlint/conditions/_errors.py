"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from typing import Any


class UnknownSatisfisfaction(Exception):
    """Unknown Satisfisfaction Exception"""

    def __init__(self, message: str, **kwargs: Any):
        super().__init__(message, **kwargs)
