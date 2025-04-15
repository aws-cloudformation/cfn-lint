"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import logging
from typing import Any, Iterator

from cfnlint.config import ConfigMixIn
from cfnlint.context.parameters import ParameterSet
from cfnlint.decode.decode import decode
from cfnlint.rules import Match
from cfnlint.rules.parameter_files.Configuration import Configuration

LOGGER = logging.getLogger(__name__)


def _parse_parameter_file(
    filename: str,
) -> dict[str, Any] | list[Match]:

    data, matches = decode(filename)

    if data is None:
        return matches

    key = "ParameterKey"
    value = "ParameterValue"
    parameters: dict[str, Any] = {}
    for parameter in data:
        if not all(p in parameter for p in [key, value]):
            return [
                Match(
                    linenumber=1,
                    columnnumber=1,
                    linenumberend=1,
                    columnnumberend=1,
                    filename=filename,
                    message=f"Parameter file {filename!r} is not supported",
                    rule=Configuration(),
                )
            ]

        parameters[parameter.get(key)] = parameter.get(value)  # type: ignore

    return parameters


def expand_parameter_files(
    config: ConfigMixIn,
) -> Iterator[tuple[ConfigMixIn | None, list[Match]]]:
    """
    Expands parameter files into an evolved config

    Args:
        config (ConfigMixIn): The configuration object containing
        settings for the deployment file scan.

    Yields:

    """

    parameters: list[ParameterSet] = []
    for parameter_file in config.parameter_files:
        parameter_data = _parse_parameter_file(parameter_file)

        if not isinstance(parameter_data, dict):
            yield None, parameter_data
            continue

        parameters.append(ParameterSet(parameter_file, parameter_data))

    if parameters:
        parameters_config = config.evolve(
            parameters=parameters,
            deployment_files=[],
        )
        yield parameters_config, []
