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
    ("name,parameters,template,expected"),
    [
        (
            "Correctly configured deployment file",
            [
                {
                    "AvailabilityZone": "us-east-1a",
                    "ImageId": "ami-12345678",
                }
            ],
            "test/fixtures/templates/integration/deployment-file-template.yaml",
            [],
        ),
        (
            "Incorrectly configured deployment file",
            [
                {
                    "Environment": "dev",
                }
            ],
            "test/fixtures/templates/integration/deployment-file-template.yaml",
            [
                Match(
                    message="'ImageId' is a required property",
                    rule=Parameters(),
                    filename=str(
                        Path(
                            "test/fixtures/templates/integration/deployment-file-template.yaml"
                        )
                    ),
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
                    filename=str(
                        Path(
                            "test/fixtures/templates/integration/deployment-file-template.yaml"
                        )
                    ),
                    linenumber=1,
                    linenumberend=1,
                    columnnumber=1,
                    columnnumberend=11,
                ),
            ],
        ),
        (
            "Multiple deployment files",
            [
                {
                    "Environment": "dev",
                },
                {
                    "AvailabilityZone": "us-east-1a",
                    "ImageId": "ami-zxyzabc123",
                    "Affinity": "dne",
                },
                {
                    "AvailabilityZone": "us-east-1a",
                    "ImageId": "ami-zxyzabc123",
                    "Tenancy": "host",
                    "Affinity": "dne",
                },
                {
                    "AvailabilityZone": "us-east-1a",
                    "ImageId": "ami-12345678",
                },
            ],
            "test/fixtures/templates/integration/deployment-file-template.yaml",
            [
                Match(
                    message="'ImageId' is a required property",
                    rule=Parameters(),
                    filename=str(
                        Path(
                            "test/fixtures/templates/integration/deployment-file-template.yaml"
                        )
                    ),
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
                    filename=str(
                        Path(
                            "test/fixtures/templates/integration/deployment-file-template.yaml"
                        )
                    ),
                    linenumber=1,
                    linenumberend=1,
                    columnnumber=1,
                    columnnumberend=11,
                ),
                Match(
                    message="'host' is not one of ['default', 'dedicated']",
                    rule=Parameters(),
                    filename=str(
                        Path(
                            "test/fixtures/templates/integration/deployment-file-template.yaml"
                        )
                    ),
                    linenumber=9,
                    linenumberend=9,
                    columnnumber=3,
                    columnnumberend=10,
                ),
                Match(
                    message=(
                        "{'Ref': 'Affinity'} is not one of ['default', 'host'] "
                        "when 'Ref' is resolved to 'dne'"
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
                        "is resolved to 'ami-zxyzabc123'"
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
def test_parameters(
    name,
    parameters,
    template,
    expected,
):

    config = ConfigMixIn(
        cli_args=[],
        parameters=parameters,
        templates=[template],
    )

    runner = Runner(config)
    results = list(runner.run())

    assert results == expected, f"{name}: {results} != {expected}"
