"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from copy import deepcopy
from typing import Iterator

from cfnlint.config import ConfigMixIn
from cfnlint.rules import Match, Rules
import cfnlint.runner.deployment_files.deployment_types
from cfnlint.decode import decode
from cfnlint.runner.template import TemplateRunner

def run_deployment_file(filename: str, config: ConfigMixIn) -> Iterator[Match]:
    """
    Run a single deployment file specified in the configuration.

    Args:
        filename (str): The filename of the deployment file to be run.
        config (ConfigMixIn): The configuration object containing
        settings for the deployment file scan.

    Yields:

    """

    data = decode(filename)

    ignore_bad_template: bool = False
    if config.ignore_bad_template:
        ignore_bad_template = True

    for plugin in cfnlint.runner.deployment_files.deployment_types.__all__:
        try:
            deployment_data = getattr(cfnlint.runner.deployment_files.deployment_types, plugin)(data)
            (template, matches) = decode(filename)
            if matches:
                if ignore_bad_template or any(
                    "E0000".startswith(x) for x in self.config.ignore_checks
                ):
                    matches = [match for match in matches if match.rule.id != "E0000"]

                yield from iter(matches)
                continue
        except Exception as e:
            print(e)
            continue

    return
    yield


def run_deployment_files(config: ConfigMixIn) -> Iterator[Match]:
    """
    Run the deployment files specified in the configuration.

    Args:
        config (ConfigMixIn): The configuration object containing
        settings for the deployment file scan.

    Yields:

    """

    ignore_bad_template: bool = False
    if config.ignore_bad_template:
        ignore_bad_template = True

    for deployment_file in config.deployment_files:
        yield from run_deployment_file(deployment_file, deepcopy(config))
