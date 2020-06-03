"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

def equalsOp(rule, propertyList):
    """ Process EQUALS operators """
    if not propertyList:
        return 'Error - Invalid Resource Type ' + rule[0]
    for prop in propertyList:
        actualValue = getProperty(prop, rule[1])
        if actualValue.strip() != str(rule[3]).strip():
            return 'Not Equal as ' + actualValue + ' does not equal ' + rule[3]
    return 'EQUALS'

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
