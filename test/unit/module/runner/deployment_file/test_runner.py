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
from cfnlint.runner.deployment_file import run_deployment_file

_filename = "deployment-file.yaml"


@pytest.mark.parametrize(
    "name, decode, validate_template_parameters, validate_template_return, expected",
    [
        (
            "A standard git sync file",
            (
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
            {
                "filename": Path("../a/path"),
                "template_parameters": [{"Foo": "Bar"}],
            },
            [],
            [],
        ),
        (
            "Bad template-file-path type",
            (
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
            ),
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
            (
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
            {
                "filename": Path("../a/path"),
                "template_parameters": [{"Foo": "Bar"}],
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
    ],
)
def test_runner(
    name, decode, validate_template_parameters, validate_template_return, expected
):

    with patch(
        "cfnlint.runner.deployment_file.runner.decode", return_value=decode
    ) as mock_decode:
        with patch(
            "cfnlint.runner.deployment_file.runner.run_template_by_file_path",
            return_value=validate_template_return,
        ) as mock_run_template_by_file_path:
            deployment = list(run_deployment_file(_filename, ConfigMixIn(), None))

            mock_decode.assert_called_once()
            if validate_template_parameters:
                mock_run_template_by_file_path.assert_called_once()
                config = mock_run_template_by_file_path.call_args_list
                assert config[0].kwargs.get(
                    "config"
                ).template_parameters == validate_template_parameters.get(
                    "template_parameters"
                )
                assert config[0].kwargs.get(
                    "filename"
                ) == validate_template_parameters.get("filename")

    assert deployment == expected, f"{name}: {deployment} != {expected}"
