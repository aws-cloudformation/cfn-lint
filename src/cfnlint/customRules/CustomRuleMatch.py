"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import RuleMatch


class CustomRuleMatch(RuleMatch):
    rule = ''
    message = ''
    path = ''
    filename = 'mqtemplate.yml'
    linenumber = '3'
    columnnumber = '4'

    def __init__(self, path, message, **kwargs):
        self.path = path
        self.message = message
        super().__init__(path, message, **kwargs)

    def set_id(self, id):
        self.rule = CustomRule(id)


class CustomRule(object):
    """ Allows creation of match objects"""
    def __init__(self, id):
        self.id = id