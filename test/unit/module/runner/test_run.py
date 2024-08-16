"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.config import ConfigMixIn
from cfnlint.runner import Runner


@pytest.mark.parametrize(
    "name,config,expected_count",
    [
        (
            "Test decode errors with multiple files",
            ConfigMixIn(
                cli_args=[
                    "-t",
                    "test/fixtures/templates/bad/duplicate.yaml",
                    "test/fixtures/templates/bad/duplicate.json",
                ]
            ),
            6,
        ),
    ],
)
def test_run(name, config, expected_count):

    runner = Runner(config)

    errs = list(runner.run())

    assert len(errs) == expected_count, f"{name}: {errs}"
