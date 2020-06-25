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
        if actualValue.strip().lower() != str(rule.value).strip().lower():
            matches.append(addMatches(template, rule, actualValue, prop, 'Must equal check failed'))
    return matches


def notEqualsOp(template, rule, propertyList):
    """ Process NOT_EQUALS operators """
    matches = []
    for prop in propertyList:
        actualValue = getProperty(prop, rule)
        if actualValue.strip().lower() == str(rule.value).strip().lower():
            matches.append(addMatches(template, rule, actualValue, prop, 'Must not equal check failed'))
    return matches


def greaterOp(template, rule, propertyList):
    """ Process >= operators """
    matches = []
    for prop in propertyList:
        actualValue = getProperty(prop, rule)
        if checkInt(actualValue.strip()) and checkInt(str(rule.value).strip()):
            if actualValue.strip().lower() < str(rule.value).strip().lower():
                matches.append(addMatches(template, rule, actualValue, prop, 'Greater than check failed'))
        else:
            matches.append(addMatches(template, rule, actualValue, prop, 'Given values are not numeric'))
    return matches


def lessOp(template, rule, propertyList):
    """ Process <= operators """
    matches = []
    for prop in propertyList:
        actualValue = getProperty(prop, rule)
        if checkInt(actualValue.strip()) and checkInt(str(rule.value).strip()):
            if int(actualValue.strip()) > int(str(rule.value).strip()):
                matches.append(addMatches(template, rule, actualValue, prop, 'Less than check failed'))
        else:
            matches.append(addMatches(template, rule, actualValue, prop, 'Given values are not numeric'))
    return matches


def InSetOp(template, rule, propertyList):
    """ Process INSET operators """
    matches = []
    for prop in propertyList:
        actualValue = getProperty(prop, rule)
        if actualValue.strip() not in rule.value:
            matches.append(addMatches(template, rule, actualValue, prop, 'In set check failed'))
    return matches


def NotInSetOp(template, rule, propertyList):
    """ Process NOT_INSET operators """
    matches = []
    for prop in propertyList:
        actualValue = getProperty(prop, rule)
        if actualValue.strip() in rule.value:
            matches.append(addMatches(template, rule, actualValue, prop, 'Not in set check failed'))
    return matches


def addMatches(template, rule, actualValue, prop, defaultMessage):
    path = prop['Path']
    path = path + rule.prop.split('.')
    message = ''
    if not rule.error_message:
        message = defaultMessage + ' comparing ' + actualValue + ' and ' + rule.value
    else:
        message = rule.error_message
    linenumbers = template.get_location_yaml(template.template, path)
    if linenumbers:
        return Match(
            linenumbers[0] + 1, linenumbers[1] + 1,
            linenumbers[2] + 1, linenumbers[3] + 1,
            template.filename, CustomRule(rule.lineNumber, rule.error_level),
            message, None)
    return Match(
        1, 1,
        1, 1,
        template.filename, CustomRule(rule.lineNumber, rule.error_level),
        message, None)


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


def checkInt(i):
    """ Python 2.7 Compatibility - There is no isnumeric() method """
    try:
        int(i)
        return True
    except ValueError:
        return False

class CustomRule(object):
    """ Allows creation of match objects"""

    def __init__(self, id, error_level):
        self.id = error_level + str(id)
