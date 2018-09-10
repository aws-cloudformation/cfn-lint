"""
  Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.

  Permission is hereby granted, free of charge, to any person obtaining a copy of this
  software and associated documentation files (the "Software"), to deal in the Software
  without restriction, including without limitation the rights to use, copy, modify,
  merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
  permit persons to whom the Software is furnished to do so.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
  INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
  PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
  HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
  OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
  SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import logging
import sys
import os
import re
from copy import deepcopy
from datetime import datetime
import six
from yaml.parser import ParserError
import cfnlint.helpers
from cfnlint.transform import Transform

LOGGER = logging.getLogger(__name__)


class CloudFormationLintRule(object):
    """CloudFormation linter rules"""

    id = ''
    shortdesc = ''
    description = ''
    source_url = ''
    tags = []

    logger = logging.getLogger(__name__)
    resource_property_types = []
    resource_sub_property_types = []

    def __repr__(self):
        return '%s: %s' % (self.id, self.shortdesc)

    def verbose(self):
        """Verbose output"""
        return '%s: %s\n%s' % (self.id, self.shortdesc, self.description)

    match = None
    match_resource_properties = None
    match_resource_sub_properties = None

    # pylint: disable=E0213
    def matching(match_function):
        """
            Does Logging for match functions
        """
        def wrapper(self, filename, cfn, *args, **kwargs):
            """Wrapper"""
            matches = []

            start = datetime.now()
            LOGGER.debug('Starting match function for rule %s at %s', self.id, start)
            # pylint: disable=E1102
            results = match_function(self, filename, cfn, *args, **kwargs)
            LOGGER.debug('Complete match function for rule %s at %s.  Ran in %s',
                         self.id, datetime.now(), datetime.now() - start)
            LOGGER.debug('Results from rule %s are %s: ', self.id, results)

            if results:
                for result in results:
                    linenumbers = cfn.get_location_yaml(cfn.template, result.path)
                    if linenumbers:
                        matches.append(Match(
                            linenumbers[0] + 1, linenumbers[1] + 1,
                            linenumbers[2] + 1, linenumbers[3] + 1,
                            filename, self, result.message))
                    else:
                        matches.append(Match(
                            1, 1,
                            1, 1,
                            filename, self, result.message))

            return matches
        return wrapper

    @matching
    # pylint: disable=W0613
    def matchall(self, filename, cfn):
        """Match the entire file"""
        if not self.match:
            return []

        return self.match(cfn)  # pylint: disable=E1102

    @matching
    # pylint: disable=W0613
    def matchall_resource_properties(self, filename, cfn, resource_properties, property_type, path):
        """ Check for resource properties type """
        if not self.match_resource_properties:
            return []

        if property_type in self.resource_property_types:
            return self.match_resource_properties(resource_properties, property_type, path, cfn)  # pylint: disable=E1102

        return []

    @matching
    # pylint: disable=W0613
    def matchall_resource_sub_properties(self, filename, cfn, resource_properties, property_type, path):
        """ Check for resource properties type """
        if not self.match_resource_sub_properties:
            return []

        if property_type in self.resource_sub_property_types:
            return self.match_resource_sub_properties(resource_properties, property_type, path, cfn)  # pylint: disable=E1102

        return []


class RulesCollection(object):
    """Collection of rules"""

    def __init__(self, ignore_rules=None):
        self.rules = []

        # Make Ignore Rules not required
        if ignore_rules:
            self.ignore_rules = ignore_rules
        else:
            self.ignore_rules = []

    def register(self, rule):
        """Register rules"""
        if self.is_rule_enabled(rule.id):
            self.rules.append(rule)

    def __iter__(self):
        return iter(self.rules)

    def __len__(self):
        return len(self.rules)

    def extend(self, more):
        """Extend rules"""
        for rule in more:
            if self.is_rule_enabled(rule.id):
                self.rules.append(rule)

    def __repr__(self):
        return '\n'.join([rule.verbose()
                          for rule in sorted(self.rules, key=lambda x: x.id)])

    def is_rule_enabled(self, rule_id):
        """ Cheks if an individual rule is valid """
        # Allowing ignoring of rules based on prefix to ignore checks
        for ignore_rule in self.ignore_rules:
            if rule_id.startswith(ignore_rule) and ignore_rule:
                return False

        return True

    def resource_property(self, filename, cfn, path, properties, resource_type, property_type):
        """Run loops in resource checks for embedded properties"""
        matches = []
        property_spec = cfnlint.helpers.RESOURCE_SPECS['us-east-1'].get('PropertyTypes')
        if property_type == 'Tag':
            property_spec_name = 'Tag'
        else:
            property_spec_name = '%s.%s' % (resource_type, property_type)
        if property_spec_name in property_spec:
            for rule in self.rules:
                try:
                    matches.extend(
                        rule.matchall_resource_sub_properties(
                            filename, cfn, properties, property_spec_name, path))
                except Exception as err:  # pylint: disable=W0703
                    if self.is_rule_enabled('E0002'):
                        message = 'Unknown exception while processing rule {}: {}'
                        matches.append(cfnlint.Match(
                            1, 1,
                            1, 1,
                            filename, cfnlint.RuleError(), message.format(rule.id, str(err))))

            resource_spec_properties = property_spec.get(property_spec_name, {}).get('Properties')
            if isinstance(properties, dict):
                for resource_property, resource_property_value in properties.items():
                    property_path = path[:] + [resource_property]
                    resource_spec_property = resource_spec_properties.get(resource_property, {})
                    if resource_property not in resource_spec_properties:
                        if resource_property == 'Fn::If':
                            if isinstance(resource_property_value, list):
                                if len(resource_property_value) == 3:
                                    for index, c_value in enumerate(resource_property_value[1:]):
                                        matches.extend(self.resource_property(
                                            filename, cfn,
                                            property_path[:] + [index + 1],
                                            c_value, resource_type, property_type))
                        continue
                    if (resource_spec_property.get('Type') == 'List' and
                            not resource_spec_properties.get('PrimitiveItemType')):
                        if isinstance(resource_property_value, (list)):
                            for index, value in enumerate(resource_property_value):
                                matches.extend(self.resource_property(
                                    filename, cfn,
                                    property_path[:] + [index],
                                    value, resource_type, resource_spec_property.get('ItemType')
                                ))
                    elif resource_spec_property.get('Type'):
                        if isinstance(resource_property_value, (dict)):
                            matches.extend(self.resource_property(
                                filename, cfn,
                                property_path,
                                resource_property_value,
                                resource_type, resource_spec_property.get('Type')
                            ))

        return matches

    def run_resource(self, filename, cfn, resource_type, resource_properties, path):
        """Run loops in resource checks for embedded properties"""
        matches = []
        resource_spec = cfnlint.helpers.RESOURCE_SPECS['us-east-1'].get('ResourceTypes')
        if resource_properties and resource_type in resource_spec:
            resource_spec_properties = resource_spec.get(resource_type, {}).get('Properties')
            for resource_property, resource_property_value in resource_properties.items():
                resource_spec_property = resource_spec_properties.get(resource_property, {})
                if resource_property not in resource_spec_properties:
                    if resource_property == 'Fn::If':
                        if isinstance(resource_property_value, list):
                            if len(resource_property_value) == 3:
                                for index, c_resource_properties in enumerate(resource_property_value[1:]):
                                    matches.extend(self.run_resource(
                                        filename, cfn, resource_type, c_resource_properties,
                                        path[:] + [resource_property, index + 1]))
                    continue
                if (resource_spec_property.get('Type') == 'List' and
                        not resource_spec_properties.get('PrimitiveItemType')):
                    if isinstance(resource_property_value, (list)):
                        for index, value in enumerate(resource_property_value):
                            matches.extend(self.resource_property(
                                filename, cfn,
                                path[:] + [resource_property, index],
                                value, resource_type, resource_spec_property.get('ItemType')
                            ))
                elif resource_spec_property.get('Type'):
                    if isinstance(resource_property_value, (dict)):
                        matches.extend(
                            self.resource_property(
                                filename, cfn,
                                path[:] + [resource_property],
                                resource_property_value,
                                resource_type, resource_spec_property.get('Type')
                            ))

        return matches

    def run(self, filename, cfn):
        """Run rules"""
        matches = []
        for rule in self.rules:
            try:
                matches.extend(rule.matchall(filename, cfn))
            except Exception as err:  # pylint: disable=W0703
                if self.is_rule_enabled('E0002'):
                    message = 'Unknown exception while processing rule {}: {}'
                    matches.append(cfnlint.Match(
                        1, 1,
                        1, 1,
                        filename, cfnlint.RuleError(), message.format(rule.id, str(err))))

        for resource_name, resource_attributes in cfn.get_resources().items():
            resource_type = resource_attributes.get('Type')
            resource_properties = resource_attributes.get('Properties', {})
            path = ['Resources', resource_name, 'Properties']
            for rule in self.rules:
                try:
                    matches.extend(
                        rule.matchall_resource_properties(
                            filename, cfn, resource_properties, resource_type, path))
                except Exception as err:  # pylint: disable=W0703
                    if self.is_rule_enabled('E0002'):
                        message = 'Unknown exception while processing rule {}: {}'
                        matches.append(cfnlint.Match(
                            1, 1,
                            1, 1,
                            filename, cfnlint.RuleError(), message.format(rule.id, str(err))))

            matches.extend(
                self.run_resource(
                    filename, cfn, resource_type, resource_properties, path))

        return matches

    @classmethod
    def create_from_directory(cls, rulesdir):
        """Create rules from directory"""
        result = cls([])
        if rulesdir != '':
            result.rules = cfnlint.helpers.load_plugins(os.path.expanduser(rulesdir))

        return result


class RuleMatch(object):
    """Rules Error"""

    def __init__(self, path, message):
        """Init"""
        self.path = path
        self.message = message

    def __eq__(self, item):
        """Override unique"""
        return ((self.path, self.message) == (item.path, item.message))

    def __hash__(self):
        """Hash for comparisons"""
        return hash((self.path, self.message))


class Match(object):
    """Match Classes"""

    def __init__(
            self, linenumber, columnnumber, linenumberend,
            columnnumberend, filename, rule, message=None):
        """Init"""
        self.linenumber = linenumber
        self.columnnumber = columnnumber
        self.linenumberend = linenumberend
        self.columnnumberend = columnnumberend
        self.filename = filename
        self.rule = rule
        self.message = message  # or rule.shortdesc

    def __repr__(self):
        """Represent"""
        formatstr = u'[{0}] ({1}) matched {2}:{3}'
        return formatstr.format(self.rule, self.message,
                                self.filename, self.linenumber)

    def __eq__(self, item):
        """Override equal to compare matches"""
        return (
            (
                self.linenumber, self.columnnumber, self.rule.id, self.message
            ) ==
            (
                item.linenumber, item.columnnumber, item.rule.id, item.message
            ))


class Template(object):
    """Class for a CloudFormation template"""

    # pylint: disable=dangerous-default-value
    def __init__(self, filename, template, regions=['us-east-1']):
        self.filename = filename
        self.template = template
        self.regions = regions
        self.sections = [
            'AWSTemplateFormatVersion',
            'Description',
            'Metadata',
            'Parameters',
            'Mappings',
            'Conditions',
            'Transform',
            'Resources',
            'Outputs',
            'Rules'
        ]

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo))
        return result

    def get_resources(self, resource_type=[]):
        """
            Get Resources
            Filter on type when specified
        """
        LOGGER.debug('Get resources from template...')
        resources = self.template.get('Resources', {})
        if not isinstance(resources, dict):
            return {}
        if isinstance(resource_type, six.string_types):
            resource_type = [resource_type]

        results = {}
        for k, v in resources.items():
            if isinstance(v, dict):
                if (v.get('Type', None) in resource_type) or (not resource_type and v.get('Type') is not None):
                    results[k] = v

        return results

    def get_parameters(self):
        """Get Resources"""
        LOGGER.debug('Get parameters from template...')
        parameters = self.template.get('Parameters', {})
        if not parameters:
            return {}

        return parameters

    def get_mappings(self):
        """Get Resources"""
        LOGGER.debug('Get mapping from template...')
        mappings = self.template.get('Mappings', {})
        if not mappings:
            return {}

        return mappings

    def get_resource_names(self):
        """Get all the Resource Names"""
        LOGGER.debug('Get the names of all resources from template...')
        results = []
        resources = self.template.get('Resources', {})
        if isinstance(resources, dict):
            for resourcename, _ in resources.items():
                results.append(resourcename)

        return results

    def get_parameter_names(self):
        """Get all Parameter Names"""
        LOGGER.debug('Get names of all parameters from template...')
        results = []
        parameters = self.template.get('Parameters', {})
        if isinstance(parameters, dict):
            for parametername, _ in parameters.items():
                results.append(parametername)

        return results

    def get_valid_refs(self):
        """Get all valid Refs"""
        LOGGER.debug('Get all valid REFs from template...')
        results = {}
        parameters = self.template.get('Parameters', {})
        if parameters:
            for name, value in parameters.items():
                if 'Type' in value:
                    element = {}
                    element['Type'] = value['Type']
                    element['From'] = 'Parameters'
                    results[name] = element
        resources = self.template.get('Resources', {})
        if resources:
            for name, value in resources.items():
                if 'Type' in value:
                    element = {}
                    element['Type'] = value['Type']
                    element['From'] = 'Resources'
                    results[name] = element

        pseudoparams = [
            'AWS::AccountId',
            'AWS::NotificationARNs',
            'AWS::NoValue',
            'AWS::Partition',
            'AWS::Region',
            'AWS::StackId',
            'AWS::StackName',
            'AWS::URLSuffix'
        ]
        for pseudoparam in pseudoparams:
            element = {}
            element['Type'] = 'Pseudo'
            element['From'] = 'Pseduo'
            results[pseudoparam] = element
        return results

    def get_valid_getatts(self):
        """Get all valid GetAtts"""
        LOGGER.debug('Get valid GetAtts from template...')
        resourcetypes = cfnlint.helpers.RESOURCE_SPECS['us-east-1'].get('ResourceTypes')
        results = {}
        resources = self.template.get('Resources', {})

        astrik_types = (
            'Custom::', 'AWS::CloudFormation::Stack',
            'AWS::Serverless::', 'AWS::CloudFormation::CustomResource'
        )
        for name, value in resources.items():
            if 'Type' in value:
                valtype = value['Type']
                if valtype.startswith(astrik_types):
                    LOGGER.debug('Cant build an appropriate getatt list from %s', valtype)
                    results[name] = {'*': {'PrimitiveItemType': 'String'}}
                else:
                    if value['Type'] in resourcetypes:
                        if 'Attributes' in resourcetypes[valtype]:
                            results[name] = {}
                            for attname, attvalue in resourcetypes[valtype]['Attributes'].items():
                                element = {}
                                element.update(attvalue)
                                results[name][attname] = element

        return results

    def _get_sub_resource_properties(self, keys, properties, path):
        """Used for recursive handling of properties in the keys"""
        LOGGER.debug('Get Sub Resource Properties from %s', keys)
        if not keys:
            result = {}
            result['Path'] = path
            result['Value'] = properties
            return [result]
        if isinstance(properties, dict):
            key = keys.pop(0)
            for key_name, key_value in properties.items():
                if key_name == key:
                    results = self._get_sub_resource_properties(keys[:], key_value, path[:] + [key_name])
                    if results:
                        return results
        elif isinstance(properties, list):
            matches = []
            for index, item in enumerate(properties):
                results = None
                if isinstance(item, dict):
                    if len(item) == 1:
                        for sub_key, sub_value in item.items():
                            if sub_key in cfnlint.helpers.CONDITION_FUNCTIONS:
                                cond_values = self.get_condition_values(sub_value)
                                results = []
                                for cond_value in cond_values:
                                    result_path = path[:] + [index, sub_key] + cond_value['Path']
                                    results.extend(
                                        self._get_sub_resource_properties(
                                            keys[:], cond_value['Value'], result_path))
                            elif sub_key == 'Ref':
                                if sub_value != 'AWS::NoValue':
                                    results = self._get_sub_resource_properties(keys[:], sub_value, path + [sub_key])
                            else:
                                results = self._get_sub_resource_properties(keys[:], sub_value, path + [sub_key])
                    else:
                        results = self._get_sub_resource_properties(keys[:], item, path + [index])
                if isinstance(results, dict):
                    matches.append(results)
                elif isinstance(results, list):
                    matches.extend(results)
            return matches

        return []

    def get_resource_properties(self, keys):
        """Filter keys of template"""
        LOGGER.debug('Get Properties from a resource: %s', keys)
        matches = []
        resourcetype = keys.pop(0)
        for resource_name, resource_value in self.get_resources(resourcetype).items():
            path = ['Resources', resource_name, 'Properties']
            properties = resource_value.get('Properties')
            if properties:
                results = self._get_sub_resource_properties(keys[:], properties, path)
                matches.extend(results)

        return matches

    # pylint: disable=dangerous-default-value
    def _search_deep_keys(self, searchText, cfndict, path):
        """Search deep for keys and get their values"""
        keys = []
        if isinstance(cfndict, dict):
            for key in cfndict:
                pathprop = path[:]
                pathprop.append(key)
                if key == searchText:
                    pathprop.append(cfndict[key])
                    keys.append(pathprop)
                    # pop the last element off for nesting of found elements for
                    # dict and list checks
                    pathprop = pathprop[:-1]
                if isinstance(cfndict[key], dict):
                    keys.extend(self._search_deep_keys(searchText, cfndict[key], pathprop))
                elif isinstance(cfndict[key], list):
                    for index, item in enumerate(cfndict[key]):
                        pathproparr = pathprop[:]
                        pathproparr.append(index)
                        keys.extend(self._search_deep_keys(searchText, item, pathproparr))
        elif isinstance(cfndict, list):
            for index, item in enumerate(cfndict):
                pathprop = path[:]
                pathprop.append(index)
                keys.extend(self._search_deep_keys(searchText, item, pathprop))

        return keys

    def search_deep_keys(self, searchText):
        """
            Search for keys in all parts of the templates
        """
        LOGGER.debug('Search for key %s as far down as the template goes', searchText)
        return (self._search_deep_keys(searchText, self.template, []))

    def get_condition_values(self, template, path=[]):
        """Evaluates conditions and brings back the values"""
        LOGGER.debug('Get condition values...')
        matches = []
        if not isinstance(template, list):
            return matches
        if not len(template) == 3:
            return matches

        for index, item in enumerate(template[1:]):
            result = {}
            result['Path'] = path[:] + [index + 1]
            if not isinstance(item, (dict, list)):
                # Just straight values and pass them through
                result['Value'] = item
                matches.append(result)
            elif len(item) == 1:
                # Checking for conditions inside of conditions
                if isinstance(item, dict):
                    for sub_key, sub_value in item.items():
                        if sub_key in cfnlint.helpers.CONDITION_FUNCTIONS:
                            results = self.get_condition_values(sub_value, result['Path'] + [sub_key])
                            if isinstance(results, list):
                                matches.extend(results)
                        elif sub_key == 'Ref':
                            if sub_value != 'AWS::NoValue':
                                result['Value'] = item
                                matches.append(result)
                        else:
                            # Return entire Item
                            result['Value'] = item
                            matches.append(result)
                else:
                    # Return entire Item
                    result['Value'] = item
                    matches.append(result)
            else:
                # Length longer than 1 means a list or object that should be fully returned
                result['Value'] = item
                matches.append(result)

        return matches

    def get_values(self, obj, key, path=[]):
        """
            Logic for getting the value of a key
            Returns None if the item isn't found
            Returns empty list if the item is found but Ref or GetAtt
            Returns all the values as a list if condition
            Returns the value if its just a string, int, boolean, etc.

        """
        LOGGER.debug('Get the value for key %s in %s', key, obj)
        matches = []

        if not isinstance(obj, dict):
            return None
        value = obj.get(key)
        if value is None:
            return None
        if isinstance(value, (dict)):
            if len(value) == 1:
                is_condition = False
                is_no_value = False
                for obj_key, obj_value in value.items():
                    if obj_key in cfnlint.helpers.CONDITION_FUNCTIONS:
                        is_condition = True
                        results = self.get_condition_values(obj_value, path[:] + [obj_key])
                        if isinstance(results, list):
                            for result in results:
                                check_obj = obj.copy()
                                check_obj[key] = result['Value']
                                matches.extend(self.get_values(check_obj, key, result['Path']))
                    elif obj_key == 'Ref' and obj_value == 'AWS::NoValue':
                        is_no_value = True
                if not is_condition and not is_no_value:
                    result = {}
                    result['Path'] = path[:]
                    result['Value'] = value
                    matches.append(result)
            else:
                result = {}
                result['Path'] = path[:]
                result['Value'] = value
                matches.append(result)
        elif isinstance(value, (list)):
            for list_index, list_value in enumerate(value):
                if isinstance(list_value, dict):
                    if len(list_value) == 1:
                        is_condition = False
                        is_no_value = False
                        for obj_key, obj_value in list_value.items():
                            if obj_key in cfnlint.helpers.CONDITION_FUNCTIONS:
                                is_condition = True
                                results = self.get_condition_values(obj_value, path[:] + [list_index, obj_key])
                                if isinstance(results, list):
                                    matches.extend(results)
                            elif obj_key == 'Ref' and obj_value == 'AWS::NoValue':
                                is_no_value = True
                        if not is_condition and not is_no_value:
                            result = {}
                            result['Path'] = path[:] + [list_index]
                            result['Value'] = list_value
                            matches.append(result)
                    else:
                        result = {}
                        result['Path'] = path[:] + [list_index]
                        result['Value'] = list_value
                        matches.append(result)
                else:
                    result = {}
                    result['Path'] = path[:] + [list_index]
                    result['Value'] = list_value
                    matches.append(result)
        else:
            result = {}
            result['Path'] = path[:]
            result['Value'] = value
            matches.append(result)

        return matches

    def _loc(self, obj):
        """Return location of object"""
        LOGGER.debug('Get location of object...')
        return (obj.start_mark.line, obj.start_mark.column, obj.end_mark.line, obj.end_mark.column)

    def get_sub_parameters(self, sub_string):
        """ Gets the parameters out of a Sub String"""
        regex = re.compile(r'\${[^!].*?}')
        string_params = regex.findall(sub_string)

        results = []
        for string_param in string_params:
            results.append(string_param[2:-1].strip())

        return results

    def get_location_yaml(self, text, path):
        """
        Get the location information
        """
        LOGGER.debug('Get location of path %s', path)
        result = None
        if len(path) > 1:
            try:
                result = self.get_location_yaml(text[path[0]], path[1:])
            except KeyError as err:
                pass
            if not result:
                try:
                    for key in text:
                        if key == path[0]:
                            result = self._loc(key)
                except AttributeError as err:
                    LOGGER.debug(err)
        else:
            try:
                for key in text:
                    if key == path[0]:
                        result = self._loc(key)
            except AttributeError as err:
                LOGGER.debug(err)
        return result

    def check_resource_property(self, resource_type, resource_property,
                                check_value=None, check_ref=None,
                                check_find_in_map=None, check_split=None,
                                check_join=None, check_sub=None, **kwargs):
        """ Check Resource Properties """
        LOGGER.debug('Check property %s for %s', resource_property, resource_type)
        matches = []
        resources = self.get_resources(resource_type=resource_type)
        for resource_name, resource_object in resources.items():
            properties = resource_object.get('Properties', {})
            if properties:
                matches.extend(
                    self.check_value(
                        obj=properties, key=resource_property,
                        path=['Resources', resource_name, 'Properties'],
                        check_value=check_value, check_ref=check_ref,
                        check_find_in_map=check_find_in_map, check_split=check_split,
                        check_join=check_join, check_sub=check_sub, **kwargs
                    )
                )
        return matches

    # pylint: disable=W0613
    def check_value(self, obj, key, path,
                    check_value=None, check_ref=None,
                    check_find_in_map=None, check_split=None, check_join=None,
                    check_import_value=None, check_sub=None,
                    **kwargs):
        """
            Check the value
        """
        LOGGER.debug('Check value %s for %s', key, obj)
        matches = []
        values_obj = self.get_values(obj=obj, key=key)
        new_path = path[:] + [key]
        if not values_obj:
            return matches
        for value_obj in values_obj:
            value = value_obj['Value']
            child_path = value_obj['Path']
            if not isinstance(value, dict):
                if check_value:
                    matches.extend(
                        check_value(
                            value=value, path=new_path[:] + child_path, **kwargs))
            else:
                if len(value) == 1:
                    for dict_name, _ in value.items():
                        # If this is a function we shouldn't fall back to a check_value check
                        if dict_name in cfnlint.helpers.FUNCTIONS:
                            # convert the function name from camel case to underscore
                            # Example: Fn::FindInMap becomes check_find_in_map
                            function_name = 'check_%s' % camel_to_snake(dict_name.replace('Fn::', ''))
                            if function_name == 'check_ref':
                                if check_ref:
                                    matches.extend(
                                        check_ref(
                                            value=value.get('Ref'), path=new_path[:] + child_path + ['Ref'],
                                            parameters=self.get_parameters(),
                                            resources=self.get_resources(),
                                            **kwargs))
                            else:
                                if locals().get(function_name):
                                    matches.extend(
                                        locals()[function_name](
                                            value=value.get(dict_name),
                                            path=new_path[:] + child_path + [dict_name],
                                            **kwargs)
                                    )
                        else:
                            if check_value:
                                matches.extend(
                                    check_value(
                                        value=value, path=new_path[:] + child_path, **kwargs))
                else:
                    if check_value:
                        matches.extend(
                            check_value(
                                value=value, path=new_path[:] + child_path, **kwargs))

        return matches


class Runner(object):
    """Run all the rules"""

    def __init__(
            self, rules, filename, template, regions, verbosity=0):

        self.rules = rules
        self.filename = filename
        self.verbosity = verbosity
        self.cfn = Template(filename, template, regions)

    def transform(self):
        """Transform logic"""
        LOGGER.debug('Transform templates if needed')

        matches = []
        transform_type = self.cfn.template.get('Transform')

        # Don't call transformation if Transform is not specified to prevent
        # useless execution of the transformation.
        # Currently locked in to SAM specific
        if transform_type == 'AWS::Serverless-2016-10-31':
            transform = Transform(self.filename, self.cfn.template, self.cfn.regions[0])
            matches = transform.transform_template()
            self.cfn.template = transform.template()

        return matches

    def run(self):
        """Run rules"""
        LOGGER.debug('Run scan of template...')
        matches = []
        if self.cfn.template is not None:
            matches.extend(
                self.rules.run(
                    self.filename, self.cfn))

        # uniq the list of incidents
        return_matches = []
        for _, match in enumerate(matches):
            if not any(match == u for u in return_matches):
                return_matches.append(match)
        return return_matches


def camel_to_snake(s):
    """
    Is it ironic that this function is written in camel case, yet it
    converts to snake case? hmm..
    """
    _underscorer1 = re.compile(r'(.)([A-Z][a-z]+)')
    _underscorer2 = re.compile('([a-z0-9])([A-Z])')
    subbed = _underscorer1.sub(r'\1_\2', s)
    return _underscorer2.sub(r'\1_\2', subbed).lower()


class ParseError(cfnlint.CloudFormationLintRule):
    """Parse Lint Rule"""
    id = 'E0000'
    shortdesc = 'Parsing error found when parsing the template'
    description = 'Checks for Null values and Duplicate values in resources'
    source_url = 'https://github.com/awslabs/cfn-python-lint'
    tags = ['base']

class TransformError(cfnlint.CloudFormationLintRule):
    """Transform Lint Rule"""
    id = 'E0001'
    shortdesc = 'Error found when transforming the template'
    description = 'Errors found when performing transformation on the template'
    source_url = 'https://github.com/awslabs/cfn-python-lint'
    tags = ['base', 'transform']

class RuleError(cfnlint.CloudFormationLintRule):
    """Rule processing Error"""
    id = 'E0002'
    shortdesc = 'Error processing rule on the template'
    description = 'Errors found when processing a rule on the template'
    source_url = 'https://github.com/awslabs/cfn-python-lint'
    tags = ['base', 'rule']
