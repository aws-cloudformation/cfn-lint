"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import logging
from copy import deepcopy
from pathlib import Path
from typing import Iterator

import cfnlint.runner.deployment_file.deployment_types
from cfnlint.config import ConfigMixIn
from cfnlint.decode import decode
from cfnlint.rules import Match, RuleMatch, Rules
from cfnlint.rules.deployment_files.Configuration import Configuration
from cfnlint.runner.template import run_template_by_file_path

LOGGER = logging.getLogger(__name__)


def run_deployment_file(
    filename: str, config: ConfigMixIn, rules: Rules
) -> Iterator[Match]:
    """
    Run a single deployment file specified in the configuration.

    Args:
        filename (str): The filename of the deployment file to be run.
        config (ConfigMixIn): The configuration object containing
        settings for the deployment file scan.

    Yields:

    """

    data, matches = decode(filename)

    if matches:
        yield from iter(matches)
        return

    ignore_bad_template: bool = False
    if config.ignore_bad_template:
        ignore_bad_template = True

    all_matches: list[RuleMatch] = []
    for plugin in cfnlint.runner.deployment_file.deployment_types.__all__:
        deployment_data, deployment_matches = getattr(
            cfnlint.runner.deployment_file.deployment_types, plugin
        )(data)
        if deployment_matches:
            all_matches.extend(deployment_matches)
            continue
        try:
            template_path = (
                (Path(filename).parent / deployment_data.template_file_path)
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
            template_path = Path(filename).parent / deployment_data.template_file_path
        template_config = deepcopy(config)
        template_config.template_parameters = [deployment_data.parameters]

        yield from run_template_by_file_path(
            filename=template_path,
            config=template_config,
            rules=rules,
            ignore_bad_template=ignore_bad_template,
        )
        return

    for match in all_matches:
        LOGGER.debug(
            f"While tring to process deployment file got error: {match.message}"
        )

    yield Match(
        linenumber=1,
        columnnumber=1,
        linenumberend=1,
        columnnumberend=1,
        filename=filename,
        message=f"Deployment file {filename!r} is not supported",
        rule=Configuration(),
    )


def run_deployment_files(config: ConfigMixIn, rules: Rules) -> Iterator[Match]:
    """
    Run the deployment files specified in the configuration.

    Args:
        config (ConfigMixIn): The configuration object containing
        settings for the deployment file scan.

    Yields:

    """

    for deployment_file in config.deployment_files:
        yield from run_deployment_file(deployment_file, deepcopy(config), rules)
