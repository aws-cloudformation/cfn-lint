"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""


def equalsOp(rule, propertyList):
    """ Process EQUALS operators """
    if not propertyList:
        return 'EQUALS'  # Resource type not found
    for prop in propertyList:
        actualValue = getProperty(prop, rule)
        if actualValue.strip() != str(rule.value).strip():
            return 'Not Equal as ' + actualValue + ' does not equal ' + rule.value
    return 'EQUALS'


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
