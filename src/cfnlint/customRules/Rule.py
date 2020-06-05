"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""


def make_rule(line):
    """ Object Maker Function """
    rule = Rule(line)
    return rule


class Rule(object):
    """ Used to organize intake from custom_rule config """
    valid = False
    resourceType = ''
    prop = ''
    operator = ''
    value = ''

    def __init__(self, line):
        self.valid = False

        if len(line) == 4:
            self.valid = True
            self.resourceType = line[0]
            self.prop = line[1]
            self.operator = line[2]
            self.value = line[3]
