"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from typing import List

from cfnlint.rules import Match, RulesCollection
from cfnlint.config import configure_logging
from cfnlint.core import get_rules
from cfnlint.decode import decode_str
from cfnlint.helpers import REGIONS
from cfnlint.runner import Runner

Matches = List[Match]


def lint(s: str, rules: RulesCollection, regions: List[str]) -> Matches:
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
        return errors

    if template is None:
        return []

    runner = Runner(
        rules=rules, filename=None, template=template, regions=regions,
        verbosity=0, mandatory_rules=None
    )
    return runner.run()


def lint_all(s: str) -> Matches:
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
        rules=get_rules([], [], ['I', 'W', 'E'], include_experimental=True),
        regions=REGIONS
    )
