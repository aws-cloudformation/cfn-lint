"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.context._conditions import Conditions


def test_conditions():
    with pytest.raises(ValueError):
        Conditions.create_from_instance([])
