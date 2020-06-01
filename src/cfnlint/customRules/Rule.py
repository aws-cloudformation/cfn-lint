"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
# pylint: disable=R0902

def make_rule(line, lineNumber, ruleset=None):
    """ Object Maker Function """
    rule = Rule(line, lineNumber, ruleset)
    return rule


class Rule(object):
    """ Used to organize intake from custom_rule config """
    valid = False
    resourceType = ''
    prop = ''
    operator = ''
    value = ''
    lineNumber = 0
    error_level = 'W'
    ruleSet = []
    error_message = ''

    def __init__(self, line, lineNumber, ruleSet):
        self.lineNumber = lineNumber
        self.valid = False
        self.ruleSet = ruleSet
        line = line.split(' ', 3)
        if len(line) == 4:
            self.valid = True
            self.resourceType = line[0]
            self.prop = line[1]
            self.operator = line[2]
            if 'WARN' in line[3]:
                self.error_level = 'W'
                self.set_arguments(line[3], 'WARN')
            elif 'ERROR' in line[3]:
                self.error_level = 'E'
                self.set_arguments(line[3], 'ERROR')
            else:
                self.process_sets(line[3])
                self.value = line[3]
        self.lineNumber = str(self.lineNumber).zfill(4)

    def set_arguments(self, argument, error):
        values = argument.split(error)
        self.value = values[0].strip()
        self.process_sets(values[0])
        if len(values) > 1:
            self.error_message = values[1]

    def process_sets(self, value):
        if len(value) > 1 and value[0] == '[' and (value[-2] == ']' or value[-1] == ']'):
            value = value[1:-2]
            value = value.split(',')
            for x in value:
                x = x.strip()
            self.ruleSet = value
