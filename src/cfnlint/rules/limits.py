"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.helpers import LIMITS
from cfnlint.rules import RuleMatch


def approaching_name_limit(cfn, section):
    """approaching name limit"""
    matches = []
    for name in cfn.template.get(section, {}):
        if LIMITS['threshold'] * LIMITS[section]['name'] < len(name) <= LIMITS[section]['name']:
            message = 'The length of ' + section[:-1] + ' name ({0}) is approaching the limit ({1})'
            matches.append(RuleMatch([section, name], message.format(len(name), LIMITS[section]['name'])))
    return matches


def approaching_number_limit(cfn, section):
    """approaching number limit"""
    matches = []
    number = cfn.template.get(section, {})
    if LIMITS['threshold'] * LIMITS[section]['number'] < len(number) <= LIMITS[section]['number']:
        message = 'The number of ' + section + ' ({0}) is approaching the limit ({1})'
        matches.append(RuleMatch([section], message.format(len(number), LIMITS[section]['number'])))
    return matches


def name_limit(cfn, section):
    """exceeding name limit"""
    matches = []
    for name in cfn.template.get(section, {}):
        if len(name) > LIMITS[section]['name']:
            message = 'The length of ' + section[:-1] + ' name ({0}) exceeds the limit ({1})'
            matches.append(RuleMatch([section, name], message.format(len(name), LIMITS[section]['name'])))
    return matches


def number_limit(cfn, section):
    """exceeding number limit"""
    matches = []
    number = cfn.template.get(section, {})
    if len(number) > LIMITS[section]['number']:
        message = 'The number of ' + section + ' ({0}) exceeds the limit ({1})'
        matches.append(RuleMatch([section], message.format(len(number), LIMITS[section]['number'])))
    return matches
