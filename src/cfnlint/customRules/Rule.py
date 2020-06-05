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
    error_message = ''

    def __init__(self, line, ruleNumber, ruleSet):
        line = line.replace('"', '')
        self.lineNumber = ruleNumber
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
        raw_value = argument.split(error)
        self.value = raw_value[0].strip()
        self.process_sets(raw_value[0])
        if len(raw_value) > 1:
            self.error_message = raw_value[1]

    def process_sets(self, raw_value):
        if len(raw_value) > 1 and raw_value[0] == '[' and (raw_value[-2] == ']' or raw_value[-1] == ']'):
            raw_value = raw_value[1:-2]
            raw_value = raw_value.split(',')
            for x in raw_value:
                x = x.strip()
            self.value = raw_value
