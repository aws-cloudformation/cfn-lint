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
from cfnlint.rules import Match, Rules
from cfnlint.runner.exceptions import CfnLintExitException
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

    for plugin in cfnlint.runner.deployment_file.deployment_types.__all__:
        try:
            deployment_data = getattr(
                cfnlint.runner.deployment_file.deployment_types, plugin
            )(data)
            template_path = Path(filename).parent / deployment_data.template_file_path
            template_config = deepcopy(config)
            template_config.template_parameters = deployment_data.parameters

            yield from run_template_by_file_path(
                template_path, template_config, rules, ignore_bad_template
            )
            return
        except Exception as e:
            LOGGER.info(e)
            continue

    raise CfnLintExitException(
        f"Deployment file {filename} didn't meet any supported deployment file format",
        1,
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
