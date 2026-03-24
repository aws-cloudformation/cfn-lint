"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from datetime import datetime
from unittest.mock import patch

import pytest

FROZEN_DATE = datetime(2026, 1, 1)

DATETIME_MODULES = [
    "cfnlint.rules.resources.lmbd.DeprecatedRuntimeCreate.datetime",
    "cfnlint.rules.resources.lmbd.DeprecatedRuntimeUpdate.datetime",
    "cfnlint.rules.resources.lmbd.DeprecatedRuntimeEol.datetime",
]


@pytest.fixture(autouse=True)
def freeze_datetime():
    patches = [patch(m) for m in DATETIME_MODULES]
    mocks = [p.start() for p in patches]
    for mock in mocks:
        mock.today.return_value = FROZEN_DATE
        mock.strptime = datetime.strptime
    yield
    for p in patches:
        p.stop()
