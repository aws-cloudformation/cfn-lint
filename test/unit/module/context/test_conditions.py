"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.context.context import _init_conditions


def test_conditions():
    with pytest.raises(ValueError):
        _init_conditions([])
