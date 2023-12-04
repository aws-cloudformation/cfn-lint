"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Iterator, List

from cfnlint.config import ConfigMixIn, ManualArgs, configure_logging
from cfnlint.decode.decode import decode_str
from cfnlint.helpers import REGION_PRIMARY, REGIONS
from cfnlint.rules import Match, Rules
from cfnlint.runner import Runner

Matches = List[Match]


def lint(
    s: str,
    rules: Rules | None = None,
    regions: List[str] | None = None,
    config: ManualArgs | None = None,
) -> Iterator[Match]:
    """Validate a string template using the specified rules and regions.

    Parameters
    ----------
    s : str
        the template string
    rules : RulesCollection
        The rules to run against s
    regions : List[str]
        The regions to test against s

    Returns
    -------
    list
        a list of errors if any were found, else an empty list
    """
    configure_logging(None, None)
    template, errors = decode_str(s)
    if errors:
        yield from iter(errors)

    if template is None:
        return

    if not regions:
        regions = [REGION_PRIMARY]

    if not config:
        config_mixin = ConfigMixIn(
            regions=regions,
        )
    else:
        config_mixin = ConfigMixIn(**config)

    runner = Runner(config_mixin)
    if isinstance(rules, Rules):
        runner.rules = rules
    yield from runner.validate_template(None, template)


def lint_all(s: str) -> Iterator[Match]:
    """Validate a string template against all regions and rules.

    Parameters
    ----------
    s : str
        the template string

    Returns
    -------
    list
        a list of errors if any were found, else an empty list
    """
    yield from lint(
        s=s,
        config=ManualArgs(
            include_checks=["I"], include_experimental=True, regions=REGIONS
        ),
    )
