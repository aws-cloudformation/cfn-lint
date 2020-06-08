"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.customRules import CustomRuleMatch


def equalsOp(rule, propertyList):
    """ Process EQUALS operators """

    if not propertyList:
        result = CustomRuleMatch.CustomRuleMatch(' ', rule.operator)
        result.set_id('E9200')
        return result  # Resource type not found

    for prop in propertyList:
        #print('Prop: ' + str(prop))
        actualValue = getProperty(prop, rule)
        #print('rule.prop: ' + rule.prop)
        if actualValue.strip() != str(rule.value).strip():
            result = CustomRuleMatch.CustomRuleMatch(prop, 'Not Equal as ' + actualValue + ' does not equal ' + rule.value)
            result.set_id('E9201')
            return result

    result = CustomRuleMatch.CustomRuleMatch(' ', rule.operator)
    result.set_id('E9202')
    return result


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
