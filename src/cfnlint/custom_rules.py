import logging
import cfnlint


LOGGER = logging.getLogger(__name__)
Operators = {'EQUALS': lambda x, y: equals(x, y)}

def check_custom_rules(filename, template):
    """ Process custom rule file """
    matches = []
    with open(filename) as customRules:
        count = 1
        for line in customRules:
            LOGGER.debug('Processing Custom Rule Line %d', count)
            line = line.replace('"', '')
            rule = line.split(' ')
            if len(rule) == 4 and rule[0][0] != '#':
                try:
                    result = Operators[rule[2]](rule, template.get_resource_properties([rule[0]]))
                    if result != rule[2]:
                        matches.append(cfnlint.rules.Match(count, '0', '0', '0', filename, CustomRule('E9999'), result, None))
                except KeyError as e:
                    matches.append(cfnlint.rules.Match(count, '0', '0', '0', filename, CustomRule('E9999'), 'Error - Invalid Operator', None))
            count += 1
    return matches

def equals(rule, propertyList):
    """ Process EQUAL operators """
    if len(propertyList) == 0:
        return 'Error - Invalid Resource Type ' + rule[0]
    for prop in propertyList:
        actualValue = getProperty(prop, rule[1])
        if actualValue.strip() != str(rule[3]).strip():
            return 'Not Equal as ' + actualValue + ' does not equal ' + rule[3]
    return 'EQUALS'


def getProperty(json, nestedProperties):
    """ Converts dot format strings to resultant values """
    nestedProperties = 'Value.' + str(nestedProperties)
    properties = nestedProperties.split(".")
    for prop in properties:
        try:
            json = json[prop]
        except KeyError as e:
            return 'The following property was not found - "%s"' % str(e)
    return str(json)

class CustomRule(object):
    def __init__(self, id):
        self.id = id


