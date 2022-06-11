"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from .config import configure_logging
from .core import get_rules
from .decode import decode_str
from .helpers import REGIONS
from .runner import Runner


def lint(s, rules, regions):
    """Validate a string template using the specified rules and regions.

    Parameters
    ----------
    s : str
        the template string
    rules : RulesCollection
        The rules to run against s
    regions : RulesCollection
        The regions to test against s

    Returns
    -------
    list
        a list of errors if any were found, else an empty list
    """
    configure_logging(None, None)
    template, errors = decode_str(s)
    if not errors:
        runner = Runner(
            rules=rules, filename=None, template=template, regions=regions,
            verbosity=0, mandatory_rules=None
        )
        errors = runner.run()
    return errors


def lint_all(s):
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
