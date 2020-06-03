"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

def equalsOp(rule, propertyList):
    """ Process EQUALS operators """
    if not propertyList:
        return 'Error - Invalid Resource Type ' + rule.resourceType
    for prop in propertyList:
        actualValue = getProperty(prop, rule.prop)
        if actualValue.strip() != str(rule.value).strip():
            return 'Not Equal as ' + actualValue + ' does not equal ' + rule.value
    return 'EQUALS'

def getProperty(json, nestedProperties):
    """ Converts dot format strings to resultant values -
    i.e inputting 'Value.InstanceSize' to nestedProperties will output the value of that specific property from json"""
    nestedProperties = 'Value.' + str(nestedProperties)
    properties = nestedProperties.split('.')
    for prop in properties:
        try:
            json = json[prop]
        except KeyError:
            return 'The following property was not found - "%s"' % nestedProperties
        except TypeError:
            return 'The following property was not found - "%s"' % nestedProperties
    return str(json)
