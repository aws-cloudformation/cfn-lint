"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from pathlib import Path
from unittest.mock import patch

import pytest

from cfnlint.config import ConfigMixIn
from cfnlint.rules import Match
from cfnlint.rules.deployment_files.Configuration import Configuration
from cfnlint.runner.deployment_file import run_deployment_files

_filename = "deployment-file.yaml"


@pytest.mark.parametrize(
    (
        "name,deployment_files,validate_template_parameters,"
        "validate_template_return,expected"
    ),
    [
        (
            "A standard git sync file",
            {
                _filename: (
                    {
                        "template-file-path": "../a/path",
                        "parameters": {
                            "Foo": "Bar",
                        },
                        "tags": {
                            "Key": "Value",
                        },
                    },
                    [],
                ),
            },
            {
                "filename": Path("../a/path"),
                "parameters": [{"Foo": "Bar"}],
            },
            [],
            [],
        ),
        (
            "Bad template-file-path type",
            {
                _filename: (
                    {
                        "template-file-path": ["../a/path"],
                        "parameters": {
                            "Foo": "Bar",
                        },
                        "tags": {
                            "Key": "Value",
                        },
                    },
                    [],
                )
            },
            {},
            [],
            [
                Match(
                    linenumber=1,
                    columnnumber=1,
                    linenumberend=1,
                    columnnumberend=1,
                    filename=_filename,
                    message=f"Deployment file {_filename!r} is not supported",
                    rule=Configuration(),
                )
            ],
        ),
        (
            "Bad template-file-path type",
            {
                _filename: (
                    {
                        "template-file-path": "../a/path",
                        "parameters": {
                            "Foo": "Bar",
                        },
                        "tags": {
                            "Key": "Value",
                        },
                    },
                    [],
                ),
            },
            {
                "filename": Path("../a/path"),
                "parameters": [{"Foo": "Bar"}],
            },
            iter(
                [
                    Match(
                        linenumber=1,
                        columnnumber=1,
                        linenumberend=1,
                        columnnumberend=1,
                        filename=_filename,
                        message=f"Deployment file {_filename!r} is not supported",
                        rule=Configuration(),
                    )
                ]
            ),
            [
                Match(
                    linenumber=1,
                    columnnumber=1,
                    linenumberend=1,
                    columnnumberend=1,
                    filename=_filename,
                    message=f"Deployment file {_filename!r} is not supported",
                    rule=Configuration(),
                )
            ],
        ),
        (
            "Bad decode",
            {
                _filename: (
                    {},
                    [
                        Match(
                            linenumber=1,
                            columnnumber=1,
                            linenumberend=1,
                            columnnumberend=1,
                            filename=_filename,
                            message=f"Deployment file {_filename!r} is not supported",
                            rule=Configuration(),
                        )
                    ],
                ),
            },
            {},
            None,
            [
                Match(
                    linenumber=1,
                    columnnumber=1,
                    linenumberend=1,
                    columnnumberend=1,
                    filename=_filename,
                    message=f"Deployment file {_filename!r} is not supported",
                    rule=Configuration(),
                )
            ],
        ),
    ],
)
def test_runner(
    name,
    deployment_files,
    validate_template_parameters,
    validate_template_return,
    expected,
):

    decode_results = [v for _, v in deployment_files.items()]
    deployment_files = {k for k, _ in deployment_files.items()}
    with patch("cfnlint.runner.deployment_file.runner.decode") as mock_decode:
        mock_decode.side_effect = decode_results
        with patch(
            "cfnlint.runner.deployment_file.runner.run_template_by_file_path",
            return_value=validate_template_return,
        ) as mock_run_template_by_file_path:
            config = ConfigMixIn([], deployment_files=deployment_files)
            deployment = list(run_deployment_files(config, None))

            for deployment_file in deployment_files:
                mock_decode.assert_called_with(deployment_file)
            if validate_template_parameters:
                mock_run_template_by_file_path.assert_called_once()
                config = mock_run_template_by_file_path.call_args_list
                assert config[0].kwargs.get(
                    "config"
                ).parameters == validate_template_parameters.get("parameters")
                assert config[0].kwargs.get(
                    "filename"
                ) == validate_template_parameters.get("filename")

    assert deployment == expected, f"{name}: {deployment} != {expected}"
