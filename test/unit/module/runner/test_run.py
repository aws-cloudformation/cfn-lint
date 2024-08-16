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
                    "--template",
                    "test/fixtures/templates/bad/duplicate.yaml",
                    "test/fixtures/templates/bad/duplicate.json",
                ]
            ),
            6,
        ),
        (
            "Test decode errors with E0000 being ignored",
            ConfigMixIn(
                cli_args=[
                    "--template",
                    "test/fixtures/templates/bad/core/parse_invalid_map.yaml",
                    "--ignore-bad-template",
                ]
            ),
            0,
        ),
        (
            "Test decode return E0000 errors",
            ConfigMixIn(
                cli_args=[
                    "--template",
                    "test/fixtures/templates/bad/core/parse_invalid_map.yaml",
                ]
            ),
            1,
        ),
    ],
)
def test_run(name, config, expected_count):

    runner = Runner(config)

    errs = list(runner.run())

    assert len(errs) == expected_count, f"{name}: {errs}"
