"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterator

import cfnlint.runner.deployment_file.deployment_types
from cfnlint.config import ConfigMixIn
from cfnlint.context.parameters import ParameterSet
from cfnlint.decode import decode
from cfnlint.rules import Match, RuleMatch
from cfnlint.rules.deployment_files.Configuration import Configuration
from cfnlint.runner.deployment_file.deployment import DeploymentFileData

LOGGER = logging.getLogger(__name__)


def _parse_deployment_file(
    filename: str,
) -> DeploymentFileData | list[Match]:

    data, matches = decode(filename)

    if data is None:
        return matches

    all_matches: list[RuleMatch] = []
    for plugin in cfnlint.runner.deployment_file.deployment_types.__all__:
        deployment_data, deployment_matches = getattr(
            cfnlint.runner.deployment_file.deployment_types, plugin
        )(data)
        if deployment_matches:
            all_matches.extend(deployment_matches)
            continue

        return deployment_data  # type: ignore

    for match in all_matches:
        LOGGER.debug(
            f"While tring to process deployment file got error: {match.message}"
        )

    return [
        Match(
            linenumber=1,
            columnnumber=1,
            linenumberend=1,
            columnnumberend=1,
            filename=filename,
            message=f"Deployment file {filename!r} is not supported",
            rule=Configuration(),
        )
    ]


def expand_deployment_files(
    config: ConfigMixIn,
) -> Iterator[tuple[ConfigMixIn | None, list[Match]]]:
    """
    Run the deployment files specified in the configuration.

    Args:
        config (ConfigMixIn): The configuration object containing
        settings for the deployment file scan.

    Yields:

    """

    deployments: dict[str, list[ParameterSet]] = {}
    for deployment_file in config.deployment_files:
        deployment_data = _parse_deployment_file(deployment_file)

        if not isinstance(deployment_data, DeploymentFileData):
            yield None, deployment_data
            continue

        try:
            template_path = (
                (Path(deployment_file).parent / deployment_data.template_file_path)
                .resolve()
                .relative_to(Path.cwd())
            )
        except ValueError:
            LOGGER.debug(
                (
                    f"Template file path {deployment_data.template_file_path!r} "
                    "is not relative to the current working directory"
                )
            )
            template_path = (
                Path(deployment_file).parent / deployment_data.template_file_path
            )

        if str(template_path) in deployments:
            deployments[str(template_path)].append(
                ParameterSet(deployment_file, deployment_data.parameters)
            )
        else:
            deployments[str(template_path)] = [
                ParameterSet(deployment_file, deployment_data.parameters)
            ]

    for path, parameter_sets in deployments.items():
        template_config = config.evolve(
            templates=[path],
            parameters=parameter_sets,
            deployment_files=[],
        )
        yield template_config, []
