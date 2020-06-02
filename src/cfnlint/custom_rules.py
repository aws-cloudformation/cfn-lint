"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
# pylint: disable=W0108
# pylint: disable=W0622
import logging
import cfnlint
import cfnlint.customRules.Operators

LOGGER = logging.getLogger(__name__)
Operator = {'EQUALS': lambda x, y: cfnlint.customRules.Operators.equalsOp(x, y),
            'PLACEHOLDER': lambda x, y: LOGGER.debug('Placeholder Op')}

def check(filename, template):
    """ Process custom rule file """
    matches = []
    with open(filename) as customRules:
        count = 1
        for line in customRules:
            LOGGER.debug('Processing Custom Rule Line %d', count)
            line = line.replace('"', '')
            rule = line.split(' ')
            if len(rule) == 4 and rule[0][0] != '#':
                resource_type = rule[0]
                operator = rule[2]
                try:
                    result = Operator[rule[2]](rule, template.get_resource_properties([resource_type]))
                    if result != operator:
                        matches.append(cfnlint.rules.Match(count, '0', '0', '0', filename, CustomRule('E9999'), result, None))
                except KeyError:
                    matches.append(cfnlint.rules.Match(count, '0', '0', '0', filename, CustomRule('E9999'),
                                                       str(rule[2]) + ' not in supported operators: [EQUALS] at ' + str(line), None))
            count += 1
    return matches

def getProperty(json, nestedProperties):
    """ Converts dot format strings to resultant values -
    i.e inputting 'Value.InstanceSize' to nestedProperties will output the value of that specific property from json"""
    nestedProperties = 'Value.' + str(nestedProperties)
    properties = nestedProperties.split('.')
    for prop in properties:
        try:
            json = json[prop]
        except KeyError as e:
            return 'The following property was not found - "%s"' % str(e)
    return str(json)

class CustomRule(object):
    """ Allows creation of match objects"""
    def __init__(self, id):
        self.__name__ = id
