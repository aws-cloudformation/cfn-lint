"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from pathlib import Path

import pytest

from cfnlint.config import ConfigMixIn
from cfnlint.rules import Match
from cfnlint.rules.deployment_files.Parameters import Parameters
from cfnlint.rules.functions.RefResolved import RefResolved
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
                    filename=str(Path("test/fixtures/deployment_files/dev.yaml")),
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
                    filename=str(Path("test/fixtures/deployment_files/dev.yaml")),
                    linenumber=3,
                    linenumberend=3,
                    columnnumber=3,
                    columnnumberend=14,
                ),
            ],
        ),
        (
            "Multiple deployment files",
            [
                "test/fixtures/deployment_files/dev.yaml",
                "test/fixtures/deployment_files/test.yaml",
                "test/fixtures/deployment_files/stage.yaml",
                "test/fixtures/deployment_files/prod.yaml",
            ],
            [
                Match(
                    message="'ImageId' is a required property",
                    rule=Parameters(),
                    filename=str(Path("test/fixtures/deployment_files/dev.yaml")),
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
                    filename=str(Path("test/fixtures/deployment_files/dev.yaml")),
                    linenumber=3,
                    linenumberend=3,
                    columnnumber=3,
                    columnnumberend=14,
                ),
                Match(
                    message="'host' is not one of ['default', 'dedicated']",
                    rule=Parameters(),
                    filename=str(Path("test/fixtures/deployment_files/stage.yaml")),
                    linenumber=5,
                    linenumberend=5,
                    columnnumber=3,
                    columnnumberend=10,
                ),
                Match(
                    message=(
                        "{'Ref': 'Affinity'} is not one of ['default', 'host'] "
                        "when 'Ref' is resolved to 'dne' from "
                        f"[{str(Path('test/fixtures/deployment_files/stage.yaml'))!r}, "
                        f"{str(Path('test/fixtures/deployment_files/test.yaml'))!r}]"
                    ),
                    rule=RefResolved(),
                    filename=str(
                        Path(
                            "test/fixtures/templates/integration/deployment-file-template.yaml"
                        )
                    ),
                    linenumber=34,
                    linenumberend=34,
                    columnnumber=7,
                    columnnumberend=15,
                ),
                Match(
                    message=(
                        "{'Ref': 'ImageId'} is not a 'AWS::EC2::Image.Id' with "
                        "pattern '^ami-([0-9a-z]{8}|[0-9a-z]{17})$' when 'Ref' "
                        "is resolved to 'ami-zxyzabc123' from "
                        f"[{str(Path('test/fixtures/deployment_files/stage.yaml'))!r}, "
                        f"{str(Path('test/fixtures/deployment_files/test.yaml'))!r}]"
                    ),
                    rule=RefResolved(),
                    filename=str(
                        Path(
                            "test/fixtures/templates/integration/deployment-file-template.yaml"
                        )
                    ),
                    linenumber=35,
                    linenumberend=35,
                    columnnumber=7,
                    columnnumberend=14,
                ),
            ],
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
