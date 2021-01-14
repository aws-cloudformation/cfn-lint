"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import re

from cfnlint.helpers import LIMITS, REGEX_ALPHANUMERIC
from cfnlint.rules import RuleMatch


def approaching_name_limit(cfn, section):
    matches = []
    for name in cfn.template.get(section, {}):
        if LIMITS['threshold'] * LIMITS[section]['name'] < len(name) <= LIMITS[section]['name']:
            message = 'The length of ' + section[:-1] + ' name ({0}) is approaching the limit ({1})'
            matches.append(RuleMatch([section, name], message.format(len(name), LIMITS[section]['name'])))
    return matches


def approaching_number_limit(cfn, section):
    matches = []
    number = cfn.get_resources() if section == 'Resources' else cfn.template.get(section, {})
    if LIMITS['threshold'] * LIMITS[section]['number'] < len(number) <= LIMITS[section]['number']:
        message = 'The number of ' + section + ' ({0}) is approaching the limit ({1})'
        matches.append(RuleMatch([section], message.format(len(number), LIMITS[section]['number'])))
    return matches


def name_limit(cfn, section):
    matches = []
    for name in cfn.template.get(section, {}):
        if len(name) > LIMITS[section]['name']:
            message = 'The length of ' + section[:-1] + ' name ({0}) exceeds the limit ({1})'
            matches.append(RuleMatch([section, name], message.format(len(name), LIMITS[section]['name'])))
    return matches


def number_limit(cfn, section):
    matches = []
    number = cfn.get_resources() if section == 'Resources' else cfn.template.get(section, {})
    if len(number) > LIMITS[section]['number']:
        message = 'The number of ' + section + ' ({0}) exceeds the limit ({1})'
        matches.append(RuleMatch([section], message.format(len(number), LIMITS[section]['number'])))
    return matches


def alphanumeric_name(cfn, section):
    matches = []
    for name, _ in cfn.template.get(section, {}).items():
        if not re.match(REGEX_ALPHANUMERIC, name):
            message = section[:-1] + ' {0} has invalid name.  Name has to be alphanumeric.'
            matches.append(RuleMatch([section, name], message.format(name)))
    return matches
