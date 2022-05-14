"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from .core import get_rules
from .helpers import REGIONS


def lint(s, rules, regions):
    """Validate a string template using the specified rules and regions.
    
    Parameters
    ----------
    s : str
        the template string
    rules : RulesCollection
        The rules to run against s
    regions : list
        The regions to test against s
    
    Returns
    -------
    list
        a list of errors if any where found, else an empty list
    """
    ...

def lint_all(s):
    """Validate a string template against all regions and rules.
    
    Parameters
    ----------
    s : str
        the template string
    
    Returns
    -------
    list
        a list of errors if any where found, else an empty list
    """
    return lint(
        s=s,
        rules=get_rules([], [], ['I', 'W', 'E'], include_experimental=True),
        regions=REGIONS
    )
