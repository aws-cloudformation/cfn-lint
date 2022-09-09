"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import os
import logging
from datetime import datetime
import importlib
import traceback
from typing import List, Optional
import cfnlint.helpers
import cfnlint.rules.custom
from cfnlint.decode.node import TemplateAttributeError
from cfnlint.template import Template


LOGGER = logging.getLogger(__name__)

def matching(match_type):
    """ Does Logging for match functions """
    def decorator(match_function):
        """ The Actual Decorator """

        def wrapper(self, filename, cfn, *args, **kwargs):
            """Wrapper"""
            matches = []

            if not getattr(self, match_type):
                return []

            if match_type == 'match_resource_properties':
                if args[1] not in self.resource_property_types:
                    return []
            elif match_type == 'match_resource_sub_properties':
                if args[1] not in self.resource_sub_property_types:
                    return []

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
                            filename, self, result.message, result))
                    else:
                        matches.append(Match(
                            1, 1,
                            1, 1,
                            filename, self, result.message, result))

            return matches
        return wrapper
    return decorator

class CloudFormationLintRule(object):
    """CloudFormation linter rules"""
    id = ''
    shortdesc = ''
    description = ''
    source_url = ''
    tags: List[str] = []
    experimental = False

    logger = logging.getLogger(__name__)

    def __init__(self):
        self.resource_property_types = []
        self.resource_sub_property_types = []
        self.config = {}  # `-X E3012:strict=false`... Show more
        self.config_definition = {}

    def __repr__(self):
        return '%s: %s' % (self.id, self.shortdesc)

    @property
    def severity(self):
        """Severity level"""
        levels = {
            'I': 'informational',
            'E': 'error',
            'W': 'warning',
        }
        return levels.get(self.id[0].upper(), 'unknown')

    def verbose(self):
        """Verbose output"""
        return '%s: %s\n%s' % (self.id, self.shortdesc, self.description)

    def initialize(self, cfn):
        """Initialize the rule"""

    def is_enabled(self, include_experimental=False, ignore_rules=None, include_rules=None,
                   mandatory_rules=None):
        """ Is the rule enabled based on the configuration """
        ignore_rules = ignore_rules or []
        include_rules = include_rules or []
        mandatory_rules = mandatory_rules or []

        # Evaluate experimental rules
        if self.experimental and not include_experimental:
            return False

        # Evaluate includes first:
        include_filter = False
        for include_rule in include_rules:
            if self.id.startswith(include_rule):
                include_filter = True
        if not include_filter:
            return False

        # Enable mandatory rules without checking for if they are ignored
        for mandatory_rule in mandatory_rules:
            if self.id.startswith(mandatory_rule):
                return True

        # Allowing ignoring of rules based on prefix to ignore checks
        for ignore_rule in ignore_rules:
            if self.id.startswith(ignore_rule) and ignore_rule:
                return False

        return True

    def configure(self, configs=None):
        """ Set the configuration """

        # set defaults
        if isinstance(self.config_definition, dict):
            for config_name, config_values in self.config_definition.items():
                self.config[config_name] = config_values['default']

        if isinstance(configs, dict):
            for key, value in configs.items():
                if key in self.config_definition:
                    if self.config_definition[key]['type'] == 'boolean':
                        self.config[key] = cfnlint.helpers.bool_compare(value, True)
                    elif self.config_definition[key]['type'] == 'string':
                        self.config[key] = str(value)
                    elif self.config_definition[key]['type'] == 'integer':
                        self.config[key] = int(value)
                    elif self.config_definition[key]['type'] == 'list':
                        self.config[key] = []
                        for l_value in value:
                            if self.config_definition[key]['itemtype'] == 'boolean':
                                self.config[key].append(cfnlint.helpers.bool_compare(l_value, True))
                            elif self.config_definition[key]['itemtype'] == 'string':
                                self.config[key].append(str(l_value))
                            elif self.config_definition[key]['itemtype'] == 'integer':
                                self.config[key].append(int(l_value))

    match = None
    match_resource_properties = None
    match_resource_sub_properties = None

    @matching('match')
    # pylint: disable=W0613
    def matchall(self, filename, cfn):
        """Match the entire file"""
        return self.match(cfn)  # pylint: disable=E1102

    @matching('match_resource_properties')
    # pylint: disable=W0613
    def matchall_resource_properties(self, filename, cfn, resource_properties, property_type, path):
        """ Check for resource properties type """
        return self.match_resource_properties(resource_properties, property_type, path, cfn)  # pylint: disable=E1102

    @matching('match_resource_sub_properties')
    # pylint: disable=W0613
    def matchall_resource_sub_properties(self, filename, cfn, resource_properties, property_type, path):
        """ Check for resource properties type """
        return self.match_resource_sub_properties(resource_properties, property_type, path, cfn)  # pylint: disable=E1102


#pylint: disable=too-many-instance-attributes
class RulesCollection(object):
    """Collection of rules"""

    def __init__(self, ignore_rules=None, include_rules=None, configure_rules=None, include_experimental=False, mandatory_rules=None):
        self.rules = []
        self.all_rules = []
        self.used_rules = set()

        self.configure(
            ignore_rules=ignore_rules,
            include_rules=include_rules,
            configure_rules=configure_rules,
            include_experimental=include_experimental,
            mandatory_rules=mandatory_rules,
            )

    def configure(self, ignore_rules=None, include_rules=None, configure_rules=None, include_experimental=False, mandatory_rules=None):
        self.rules = []
        # Whether "experimental" rules should be added
        self.include_experimental = include_experimental

        # Make Ignore Rules not required
        self.ignore_rules = ignore_rules or []
        self.include_rules = include_rules or []
        self.mandatory_rules = mandatory_rules or []
        self.configure_rules = configure_rules or {}
        # by default include 'W' and 'E'
        # 'I' has to be included manually for backwards compabitility
        # Have to add W, E here because integrations don't use config
        for default_rule in ['W', 'E']:
            if default_rule not in self.include_rules:
                self.include_rules.extend([default_rule])

        for rule in self.all_rules:
            self.__register(rule)

    def __register(self, rule):
        """ Register and configure the rule """
        if self.is_rule_enabled(rule):
            self.used_rules.add(rule.id)
            self.rules.append(rule)
            rule.configure(self.configure_rules.get(rule.id, None))

    def register(self, rule):
        """Register rules"""
        self.all_rules.append(rule)
        self.__register(rule)

    def __iter__(self):
        return iter(self.rules)

    def __len__(self):
        return len(self.rules)

    def extend(self, more):
        """Extend rules"""
        for rule in more:
            self.register(rule)

    def __repr__(self):
        return '\n'.join([rule.verbose()
                          for rule in sorted(self.rules, key=lambda x: x.id)])

    def is_rule_enabled(self, rule):
        """ Checks if an individual rule is valid """
        return rule.is_enabled(self.include_experimental, self.ignore_rules,
                               self.include_rules, self.mandatory_rules)

    # pylint: disable=inconsistent-return-statements
    def run_check(self, check, filename, rule_id, *args):
        """ Run a check """
        try:
            return check(*args)
        except TemplateAttributeError as err:
            LOGGER.debug(str(err))
            return []
        except Exception as err:  # pylint: disable=W0703
            if self.is_rule_enabled(RuleError()):
                # In debug mode, print the error include complete stack trace
                if LOGGER.getEffectiveLevel() == logging.DEBUG:
                    error_message = traceback.format_exc()
                else:
                    error_message = str(err)
                message = 'Unknown exception while processing rule {}: {}'
                return [
                    Match(
                        1, 1, 1, 1,
                        filename, RuleError(), message.format(rule_id, error_message))]

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
                if isinstance(properties, dict):
                    if len(properties) == 1:
                        for k, _ in properties.items():
                            if k != 'Fn::If':
                                matches.extend(
                                    self.run_check(
                                        rule.matchall_resource_sub_properties, filename, rule.id,
                                        filename, cfn, properties, property_spec_name, path
                                    )
                                )
                    else:
                        matches.extend(
                            self.run_check(
                                rule.matchall_resource_sub_properties, filename, rule.id,
                                filename, cfn, properties, property_spec_name, path
                            )
                        )
                else:
                    matches.extend(
                        self.run_check(
                            rule.matchall_resource_sub_properties, filename, rule.id,
                            filename, cfn, properties, property_spec_name, path
                        )
                    )

            resource_spec_properties = property_spec.get(property_spec_name, {}).get('Properties')
            if not resource_spec_properties:
                if property_spec.get(property_spec_name, {}).get('Type') == 'List':
                    if isinstance(properties, list):
                        property_type = property_spec.get(property_spec_name, {}).get('ItemType')
                        for index, item in enumerate(properties):
                            matches.extend(self.resource_property(
                                filename, cfn,
                                path[:] + [index],
                                item, resource_type, property_type))
                return matches
            if isinstance(properties, dict):
                for resource_property, resource_property_value in properties.items():
                    property_path = path[:] + [resource_property]
                    resource_spec_property = resource_spec_properties.get(resource_property, {})
                    if resource_property not in resource_spec_properties:
                        if resource_property == 'Fn::If':
                            if isinstance(resource_property_value, list):
                                if len(resource_property_value) == 3:
                                    for index, c_value in enumerate(resource_property_value[1:]):
                                        if isinstance(c_value, list):
                                            for s_i, c_l_value in enumerate(c_value):
                                                matches.extend(self.resource_property(
                                                    filename, cfn,
                                                    property_path[:] + [index + 1] + [s_i],
                                                    c_l_value, resource_type, property_type))
                                        else:
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
        if resource_properties is not None and resource_type in resource_spec:
            resource_spec_properties = resource_spec.get(resource_type, {}).get('Properties')
            items_safe = resource_properties.items_safe(path, type_t=(dict))
            for resource_properties_safe, path_safe in items_safe:
                for resource_property, resource_property_value in resource_properties_safe.items():
                    resource_spec_property = resource_spec_properties.get(resource_property, {})
                    if (resource_spec_property.get('Type') == 'List' and
                            not resource_spec_properties.get('PrimitiveItemType')):
                        if isinstance(resource_property_value, (list)):
                            for index, value in enumerate(resource_property_value):
                                matches.extend(self.resource_property(
                                    filename, cfn,
                                    path_safe[:] + [resource_property, index],
                                    value, resource_type, resource_spec_property.get('ItemType')
                                ))
                    elif resource_spec_property.get('Type'):
                        if isinstance(resource_property_value, (dict)):
                            matches.extend(
                                self.resource_property(
                                    filename, cfn,
                                    path_safe[:] + [resource_property],
                                    resource_property_value,
                                    resource_type, resource_spec_property.get('Type')
                                ))

        return matches

    def run(self, filename: Optional[str], cfn: Template):
        """Run rules"""
        matches = []
        for rule in self.rules:
            rule.initialize(cfn)

        for rule in self.rules:
            matches.extend(
                self.run_check(
                    rule.matchall, filename, rule.id, filename, cfn
                )
            )

        for resource_name, resource_attributes in cfn.get_resources().items():
            resource_type = resource_attributes.get('Type')
            resource_properties = resource_attributes.get('Properties')
            if isinstance(resource_type, str) and isinstance(resource_properties, dict):
                path = ['Resources', resource_name, 'Properties']
                for rule in self.rules:
                    matches.extend(
                        self.run_check(
                            rule.matchall_resource_properties, filename, rule.id,
                            filename, cfn, resource_properties, resource_type, path
                        )
                    )

                matches.extend(
                    self.run_resource(
                        filename, cfn, resource_type, resource_properties, path))

        return matches

    def create_from_module(self, modpath):
        """Create rules from a module import path"""
        mod = importlib.import_module(modpath)
        self.extend(cfnlint.helpers.create_rules(mod))

    def create_from_directory(self, rulesdir):
        """Create rules from directory"""
        result = []
        if rulesdir != '':
            result = cfnlint.helpers.load_plugins(os.path.expanduser(rulesdir))
        self.extend(result)

    def create_from_custom_rules_file(self, custom_rules_file):
        """Create rules from custom rules file """
        custom_rules = []
        if custom_rules_file:
            with open(custom_rules_file, encoding='utf-8') as customRules:
                line_number = 1
                for line in customRules:
                    LOGGER.debug('Processing Custom Rule Line %d', line_number)
                    custom_rule = cfnlint.rules.custom.make_rule(line, line_number)
                    if custom_rule:
                        custom_rules.append(custom_rule)
                    line_number += 1

        self.extend(custom_rules)


class RuleMatch(object):
    """Rules Error"""

    def __init__(self, path, message, **kwargs):
        """Init"""
        self.path = path
        self.path_string = '/'.join(map(str, path))
        self.message = message
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __eq__(self, item):
        """Override unique"""
        return ((self.path, self.message) == (item.path, item.message))

    def __hash__(self):
        """Hash for comparisons"""
        return hash((self.path, self.message))


class Match(object):  # pylint: disable=R0902
    """Match Classes"""

    def __init__(
            self, linenumber, columnnumber, linenumberend,
            columnnumberend, filename, rule, message=None, rulematch_obj=None):
        """Init"""
        self.linenumber = linenumber
        """Starting line number of the region this match spans"""
        self.columnnumber = columnnumber
        """Starting line number of the region this match spans"""
        self.linenumberend = linenumberend
        """Ending line number of the region this match spans"""
        self.columnnumberend = columnnumberend
        """Ending column number of the region this match spans"""
        self.filename = filename
        """Name of the filename associated with this match, or None if there is no such file"""
        self.rule = rule
        """The rule of this match"""
        self.message = message  # or rule.shortdesc
        """The message of this match"""
        if rulematch_obj:
            for k, v in vars(rulematch_obj).items():
                if not hasattr(self, k):
                    setattr(self, k, v)

    def __repr__(self):
        """Represent"""
        file_str = self.filename + ':' if self.filename else ''
        formatstr = u'[{0}] ({1}) matched {2}{3}'
        return formatstr.format(self.rule, self.message,
                                file_str, self.linenumber)

    def __eq__(self, item):
        """Override equal to compare matches"""
        return (
            (
                self.linenumber, self.columnnumber, self.rule.id, self.message
            ) ==
            (
                item.linenumber, item.columnnumber, item.rule.id, item.message
            ))


class ParseError(CloudFormationLintRule):
    """Parse Lint Rule"""
    id = 'E0000'
    shortdesc = 'Parsing error found when parsing the template'
    description = 'Checks for JSON/YAML formatting errors in your template'
    source_url = 'https://github.com/aws-cloudformation/cfn-python-lint'
    tags = ['base']


class TransformError(CloudFormationLintRule):
    """Transform Lint Rule"""
    id = 'E0001'
    shortdesc = 'Error found when transforming the template'
    description = 'Errors found when performing transformation on the template'
    source_url = 'https://github.com/aws-cloudformation/cfn-python-lint'
    tags = ['base', 'transform']


class RuleError(CloudFormationLintRule):
    """Rule processing Error"""
    id = 'E0002'
    shortdesc = 'Error processing rule on the template'
    description = 'Errors found when processing a rule on the template'
    source_url = 'https://github.com/aws-cloudformation/cfn-python-lint'
    tags = ['base', 'rule']
