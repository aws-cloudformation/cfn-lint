"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.config import ConfigMixIn
from cfnlint.rules import Match
from cfnlint.rules.deployment_files.Parameters import Parameters
from cfnlint.runner import Runner


@pytest.mark.parametrize(
    ("name,deployment_files,expected"),
    [
        (
            "Correctly configured deployment file",
            ["test/fixtures/deployment_files/prod.yaml"],
            [],
        ),
        (
            "Incorrectly configured deployment file",
            ["test/fixtures/deployment_files/dev.yaml"],
            [
                Match(
                    message="'ImageId' is a required property",
                    rule=Parameters(),
                    filename="test/fixtures/deployment_files/dev.yaml",
                    linenumber=1,
                    linenumberend=1,
                    columnnumber=1,
                    columnnumberend=11,
                ),
                Match(
                    message=(
                        "Additional properties are not allowed "
                        "('Environment' was unexpected)"
                    ),
                    rule=Parameters(),
                    filename="test/fixtures/deployment_files/dev.yaml",
                    linenumber=3,
                    linenumberend=3,
                    columnnumber=3,
                    columnnumberend=14,
                ),
            ],
        ),
        (
            "Multiple deployment files",
            ["test/fixtures/deployment_files/prod.yaml"],
            [],
        ),
    ],
)
def test_deployment_files(
    name,
    deployment_files,
    expected,
):

    config = ConfigMixIn(
        cli_args=[],
        deployment_files=deployment_files,
    )

    runner = Runner(config)
    results = list(runner.run())

    assert results == expected, f"{name}: {results} != {expected}"
