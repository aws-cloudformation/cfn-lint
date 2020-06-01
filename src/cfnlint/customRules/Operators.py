import cfnlint.custom_rules


def equalsOp(rule, propertyList):
    """ Process EQUALS operators """
    if len(propertyList) == 0:
        return 'Error - Invalid Resource Type ' + rule[0]
    for prop in propertyList:
        actualValue = cfnlint.custom_rules.getProperty(prop, rule[1])
        if actualValue.strip() != str(rule[3]).strip():
            return 'Not Equal as ' + actualValue + ' does not equal ' + rule[3]
    return 'EQUALS'

