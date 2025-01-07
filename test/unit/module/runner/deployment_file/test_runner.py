"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from unittest.mock import MagicMock, PropertyMock, patch

import pytest

from cfnlint.config import ConfigMixIn
from cfnlint.context import ParameterSet
from cfnlint.rules import Match
from cfnlint.rules.deployment_files.Configuration import Configuration
from cfnlint.runner.deployment_file import expand_deployment_files

_filename_dev = "deployment-dev.yaml"
_filename_prod = "deployment-prod.yaml"


def mock_glob(value, recursive):
    return [value]


@pytest.mark.parametrize(
    ("name,deployment_files,expected"),
    [
        (
            "A standard git sync file",
            {
                _filename_dev: (
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
            [
                (
                    ConfigMixIn(
                        [],
                        deployment_files=[_filename_dev],
                        parameters=[
                            ParameterSet(
                                source=_filename_dev, parameters={"Foo": "Bar"}
                            )
                        ],
                        templates=[
                            "../a/path",
                        ],
                    ),
                    [],
                )
            ],
        ),
        (
            "Multiple standard git sync file with same template path",
            {
                _filename_dev: (
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
                _filename_prod: (
                    {
                        "template-file-path": "../a/path",
                        "parameters": {
                            "Foo": "Foo",
                        },
                        "tags": {
                            "Key": "Value",
                        },
                    },
                    [],
                ),
            },
            [
                (
                    ConfigMixIn(
                        [],
                        deployment_files=[_filename_dev, _filename_prod],
                        parameters=[
                            ParameterSet(
                                source=_filename_dev, parameters={"Foo": "Bar"}
                            ),
                            ParameterSet(
                                source=_filename_prod, parameters={"Foo": "Foo"}
                            ),
                        ],
                        templates=[
                            "../a/path",
                        ],
                    ),
                    [],
                ),
            ],
        ),
        (
            "Multiple standard git sync file with a different template path",
            {
                _filename_dev: (
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
                _filename_prod: (
                    {
                        "template-file-path": "../b/path",
                        "parameters": {
                            "Foo": "Foo",
                        },
                        "tags": {
                            "Key": "Value",
                        },
                    },
                    [],
                ),
            },
            [
                (
                    ConfigMixIn(
                        [],
                        deployment_files=[_filename_dev],
                        parameters=[
                            ParameterSet(
                                source=_filename_dev, parameters={"Foo": "Bar"}
                            ),
                        ],
                        templates=[
                            "../a/path",
                        ],
                    ),
                    [],
                ),
                (
                    ConfigMixIn(
                        [],
                        deployment_files=[_filename_prod],
                        parameters=[
                            ParameterSet(
                                source=_filename_prod, parameters={"Foo": "Foo"}
                            ),
                        ],
                        templates=[
                            "../b/path",
                        ],
                    ),
                    [],
                ),
            ],
        ),
        (
            "Bad template-file-path type",
            {
                _filename_dev: (
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
            [
                (
                    None,
                    [
                        Match(
                            linenumber=1,
                            columnnumber=1,
                            linenumberend=1,
                            columnnumberend=1,
                            filename=_filename_dev,
                            message=(
                                f"Deployment file {_filename_dev!r} " "is not supported"
                            ),
                            rule=Configuration(),
                        )
                    ],
                )
            ],
        ),
        (
            "Bad decode",
            {
                _filename_dev: (
                    None,
                    [
                        Match(
                            linenumber=1,
                            columnnumber=1,
                            linenumberend=1,
                            columnnumberend=1,
                            filename=_filename_dev,
                            message="Random failure",
                            rule=Configuration(),
                        )
                    ],
                ),
            },
            [
                (
                    None,
                    [
                        Match(
                            linenumber=1,
                            columnnumber=1,
                            linenumberend=1,
                            columnnumberend=1,
                            filename=_filename_dev,
                            message="Random failure",
                            rule=Configuration(),
                        ),
                    ],
                ),
            ],
        ),
    ],
)
def test_runner(
    name,
    deployment_files,
    expected,
):

    decode_results = [v for _, v in deployment_files.items()]
    deployment_files = [k for k, _ in deployment_files.items()]
    with patch("glob.glob", MagicMock(side_effect=mock_glob)):

        with patch(
            "cfnlint.config.ConfigMixIn.deployment_files", new_callable=PropertyMock
        ) as mock_deployment_files:
            with patch("cfnlint.runner.deployment_file.runner.decode") as mock_decode:
                mock_deployment_files.return_value = deployment_files
                mock_decode.side_effect = decode_results
                config = ConfigMixIn([], deployment_files=deployment_files)

                deployments = list(expand_deployment_files(config))

                for deployment_file in deployment_files:
                    mock_decode.assert_any_call(deployment_file)

                assert deployments == expected, f"{name}: {deployments} != {expected}"
