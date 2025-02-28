"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from unittest.mock import MagicMock, PropertyMock, patch

import pytest

from cfnlint.config import ConfigMixIn
from cfnlint.context import ParameterSet
from cfnlint.rules import Match
from cfnlint.rules.parameter_files.Configuration import Configuration
from cfnlint.runner.parameter_file import expand_parameter_files

_filename_dev = "parameters-dev.json"
_filename_prod = "parameters-prod.json"


def mock_glob(value, recursive):
    return [value]


@pytest.mark.parametrize(
    ("name,parameter_files,expected"),
    [
        (
            "A standard parameter file",
            {
                _filename_dev: (
                    [
                        {
                            "ParameterKey": "Foo",
                            "ParameterValue": "Bar",
                        }
                    ],
                    [],
                ),
            },
            [
                (
                    ConfigMixIn(
                        [],
                        parameter_files=[_filename_dev],
                        parameters=[
                            ParameterSet(
                                source=_filename_dev, parameters={"Foo": "Bar"}
                            )
                        ],
                    ),
                    [],
                )
            ],
        ),
        (
            "Multiple standard parameter files",
            {
                _filename_dev: (
                    [
                        {
                            "ParameterKey": "Foo",
                            "ParameterValue": "Bar",
                        }
                    ],
                    [],
                ),
                _filename_prod: (
                    [
                        {
                            "ParameterKey": "One",
                            "ParameterValue": "Two",
                        }
                    ],
                    [],
                ),
            },
            [
                (
                    ConfigMixIn(
                        [],
                        parameter_files=[_filename_dev, _filename_prod],
                        parameters=[
                            ParameterSet(
                                source=_filename_dev, parameters={"Foo": "Bar"}
                            ),
                            ParameterSet(
                                source=_filename_prod, parameters={"One": "Two"}
                            ),
                        ],
                    ),
                    [],
                ),
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
                            message=(
                                "Parameter file 'parameters-dev.json' "
                                "is not supported"
                            ),
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
                            message=(
                                "Parameter file 'parameters-dev.json' "
                                "is not supported"
                            ),
                            rule=Configuration(),
                        ),
                    ],
                ),
            ],
        ),
        (
            "Bad structure",
            {
                _filename_dev: (
                    [
                        {
                            "Key": "Foo",
                            "Value": "Bar",
                        }
                    ],
                    [],
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
                            message=(
                                "Parameter file 'parameters-dev.json' "
                                "is not supported"
                            ),
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
    parameter_files,
    expected,
):

    decode_results = [v for _, v in parameter_files.items()]
    parameter_files = [k for k, _ in parameter_files.items()]
    with patch("glob.glob", MagicMock(side_effect=mock_glob)):

        with patch(
            "cfnlint.config.ConfigMixIn.parameter_files", new_callable=PropertyMock
        ) as mock_parameter_files:
            with patch("cfnlint.runner.parameter_file.runner.decode") as mock_decode:
                mock_parameter_files.return_value = parameter_files
                mock_decode.side_effect = decode_results
                config = ConfigMixIn([], parameter_files=parameter_files)

                configs = list(expand_parameter_files(config))

                for parameter_file in parameter_files:
                    mock_decode.assert_any_call(parameter_file)

                assert configs == expected, f"{name}: {configs} != {expected}"
