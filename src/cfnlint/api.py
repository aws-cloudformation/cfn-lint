"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import List

from cfnlint.config import ConfigMixIn, ManualArgs
from cfnlint.decode.decode import decode_str
from cfnlint.helpers import REGION_PRIMARY, REGIONS
from cfnlint.rules import Match, RulesCollection
from cfnlint.runner import Runner, TemplateRunner

Matches = List[Match]


def lint(
    s: str,
    rules: RulesCollection | None = None,
    regions: list[str] | None = None,
    config: ManualArgs | None = None,
) -> list[Match]:
    """Validate a string template using the specified rules and regions.

    Parameters
    ----------
    s : str
        the template string
    rules : RulesCollection
        The rules to run against s
    regions : list[str]
        The regions to test against s

    Returns
    -------
    list
        a list of errors if any were found, else an empty list
    """
    template, errors = decode_str(s)
    if errors:
        return errors

    if template is None:
        return []

    if not regions:
        regions = [REGION_PRIMARY]

    if not config:
        config_mixin = ConfigMixIn(
            regions=regions,
        )
    else:
        config_mixin = ConfigMixIn(**config)

    if isinstance(rules, RulesCollection):
        template_runner = TemplateRunner(None, template, config_mixin, rules)  # type: ignore # noqa: E501
        return list(template_runner.run())

    runner = Runner(config_mixin)
    return list(runner.validate_template(None, template))


def lint_all(s: str) -> list[Match]:
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
    return lint(
        s=s,
        config=ManualArgs(
            include_checks=["I"], include_experimental=True, regions=REGIONS
        ),
    )
