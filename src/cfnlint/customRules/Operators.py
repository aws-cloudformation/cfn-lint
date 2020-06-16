"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
# pylint: disable=W0622
from cfnlint.rules import Match


def equalsOp(template, rule, propertyList):
    """ Process EQUALS operators """
    matches = []

    for prop in propertyList:
        actualValue = getProperty(prop, rule)
        if actualValue.strip() != str(rule.value).strip():
            path = prop['Path']
            path = path + rule.prop.split('.')
            linenumbers = template.get_location_yaml(template.template, path)
            if linenumbers:
                matches.append(Match(
                    linenumbers[0] + 1, linenumbers[1] + 1,
                    linenumbers[2] + 1, linenumbers[3] + 1,
                    template.filename, CustomRule('E9201'),
                    'Not Equal as ' + actualValue + ' does not equal ' + rule.value, None))
            else:
                matches.append(Match(
                    1, 1,
                    1, 1,
                    template.filename, CustomRule('E9201'),
                    'Not Equal as ' + actualValue + ' does not equal ' + rule.value, None))
    return matches


def getProperty(json, rule):
    """ Converts dot format strings to resultant values -
    i.e inputting 'Value.InstanceSize' to nestedProperties will output the value of that specific property from json"""
    nestedProperties = 'Value.' + str(rule.prop)
    properties = nestedProperties.split('.')
    for prop in properties:
        try:
            json = json[prop]
        except KeyError:
            return rule.value  # Property type not found
        except TypeError:
            return rule.value  # Property type not found
    return str(json)


class CustomRule(object):
    """ Allows creation of match objects"""

    def __init__(self, id):
        self.id = id
