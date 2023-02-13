"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import importlib
import logging
import os
import traceback
from datetime import datetime
from typing import Any, Callable, Dict, List, MutableSet, Optional, Tuple, Union

import cfnlint.helpers
import cfnlint.rules.custom
from cfnlint.decode.exceptions import TemplateAttributeError
from cfnlint.exceptions import DuplicateRuleError
<<<<<<< HEAD
from cfnlint.match import Match
from cfnlint.template import Template
=======
from cfnlint.template.template import Template
>>>>>>> 83f57c754 (Convert to using CloudFormation provider schemas)

LOGGER = logging.getLogger(__name__)


class RuleMatch:
    """Rules Error"""

    def __init__(self, path, message, **kwargs):
        """Init"""
        self.path = path
        self.path_string = "/".join(map(str, path))
        self.message = message
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __eq__(self, item):
        """Override unique"""
        return (self.path, self.message) == (item.path, item.message)

    def __hash__(self):
        """Hash for comparisons"""
        return hash((self.path, self.message))


def matching(match_type: Any):
    """Does Logging for match functions"""

    def decorator(match_function):
        """The Actual Decorator"""

        def wrapper(self, filename: str, cfn: Template, *args, **kwargs):
            """Wrapper"""
            matches = []

            if not getattr(self, match_type):
                return []

            if match_type == "match_resource_properties":
                if args[1] not in self.resource_property_types:
                    return []
            elif match_type == "match_resource_sub_properties":
                if args[1] not in self.resource_sub_property_types:
                    return []

            start = datetime.now()
            LOGGER.debug("Starting match function for rule %s at %s", self.id, start)
            # pylint: disable=E1102
            results = match_function(self, filename, cfn, *args, **kwargs)
            LOGGER.debug(
                "Complete match function for rule %s at %s.  Ran in %s",
                self.id,
                datetime.now(),
                datetime.now() - start,
            )
            LOGGER.debug("Results from rule %s are %s: ", self.id, results)

            if results:
                for result in results:
                    error_rule = self
                    if hasattr(result, "rule"):
                        error_rule = result.rule
                    linenumbers: Union[Tuple[int, int, int, int], None] = None
                    if hasattr(result, "location"):
                        linenumbers = result.location
                    else:
                        linenumbers = cfn.get_location_yaml(cfn.template, result.path)
                    if linenumbers:
                        matches.append(
                            Match(
                                linenumbers[0] + 1,
                                linenumbers[1] + 1,
                                linenumbers[2] + 1,
                                linenumbers[3] + 1,
                                filename,
                                error_rule,
                                result.message,
                                result,
                            )
                        )
                    else:
                        matches.append(
                            Match(
                                1, 1, 1, 1, filename, error_rule, result.message, result
                            )
                        )

            return matches

        return wrapper

    return decorator


class CloudFormationLintRule:
    """CloudFormation linter rules"""

    id: str = ""
    shortdesc: str = ""
    description: str = ""
    source_url: str = ""
    tags: List[str] = []
    experimental: bool = False
    child_rules: Dict[str, Any] = {}

    logger = logging.getLogger(__name__)

    def __init__(self):
        self.resource_property_types = []
        self.resource_sub_property_types = []
        self.config = {}  # `-X E3012:strict=false`... Show more
        self.config_definition = {}

    def __repr__(self):
        return f"{self.id}: {self.shortdesc}"

    @property
    def severity(self):
        """Severity level"""
        levels = {
            "I": "informational",
            "E": "error",
            "W": "warning",
        }
        return levels.get(self.id[0].upper(), "unknown")

    def verbose(self):
        """Verbose output"""
        return f"{self.id}: {self.shortdesc}\n{self.description}"

    def initialize(self, cfn):
        """Initialize the rule"""

    def is_enabled(
        self,
        include_experimental=False,
        ignore_rules=None,
        include_rules=None,
        mandatory_rules=None,
    ):
        """Is the rule enabled based on the configuration"""
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

    def configure(self, configs=None, experimental=False):
        """Set the configuration"""

        # set defaults
        if isinstance(self.config_definition, dict):
            for config_name, config_values in self.config_definition.items():
                self.config[config_name] = config_values["default"]

        # set experimental if the rule is asking for it
        if "experimental" in self.config_definition:
            if self.config_definition["experimental"]["type"] == "boolean":
                self.config["experimental"] = cfnlint.helpers.bool_compare(
                    experimental, True
                )

        if isinstance(configs, dict):
            for key, value in configs.items():
                if key in self.config_definition:
                    if self.config_definition[key]["type"] == "boolean":
                        self.config[key] = cfnlint.helpers.bool_compare(value, True)
                    elif self.config_definition[key]["type"] == "string":
                        self.config[key] = str(value)
                    elif self.config_definition[key]["type"] == "integer":
                        self.config[key] = int(value)
                    elif self.config_definition[key]["type"] == "list":
                        self.config[key] = []
                        for l_value in value:
                            if self.config_definition[key]["itemtype"] == "boolean":
                                self.config[key].append(
                                    cfnlint.helpers.bool_compare(l_value, True)
                                )
                            elif self.config_definition[key]["itemtype"] == "string":
                                self.config[key].append(str(l_value))
                            elif self.config_definition[key]["itemtype"] == "integer":
                                self.config[key].append(int(l_value))

    match: Callable[[Template], List[RuleMatch]] = None  # type: ignore
    match_resource_properties: Callable[[Dict, str, List[str], Template], List[RuleMatch]] = None  # type: ignore
    match_resource_sub_properties: Callable[[Dict, str, List[str], Template], List[RuleMatch]] = None  # type: ignore

    @matching("match")
    # pylint: disable=W0613
    def matchall(self, filename, cfn):
        """Match the entire file"""
        return self.match(cfn)  # pylint: disable=E1102

    @matching("match_resource_properties")
    # pylint: disable=W0613
    def matchall_resource_properties(
        self, filename, cfn, resource_properties, property_type, path
    ):
        """Check for resource properties type"""
        return self.match_resource_properties(  # pylint: disable=E1102
            resource_properties, property_type, path, cfn
        )

    @matching("match_resource_sub_properties")
    # pylint: disable=W0613
    def matchall_resource_sub_properties(
        self, filename, cfn, resource_properties, property_type, path
    ):
        """Check for resource properties type"""
        return self.match_resource_sub_properties(  # pylint: disable=E1102
            resource_properties, property_type, path, cfn
        )


# pylint: disable=too-many-instance-attributes
class RulesCollection:
    """Collection of rules"""

    def __init__(
        self,
        ignore_rules: Union[List[str], None] = None,
        include_rules: Union[List[str], None] = None,
        configure_rules: Any = None,
        include_experimental: bool = False,
        mandatory_rules: Union[List[str], None] = None,
    ):
        self.rules: Dict[str, CloudFormationLintRule] = {}
        self.all_rules: Dict[str, CloudFormationLintRule] = {}
        self.used_rules: MutableSet[str] = set()

        self.configure(
            ignore_rules=ignore_rules,
            include_rules=include_rules,
            configure_rules=configure_rules,
            include_experimental=include_experimental,
            mandatory_rules=mandatory_rules,
        )

    def configure(
        self,
        ignore_rules: Union[List[str], None] = None,
        include_rules: Union[List[str], None] = None,
        configure_rules: Any = None,
        include_experimental: bool = False,
        mandatory_rules: Union[List[str], None] = None,
    ):
        self.rules = {}
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
        for default_rule in ["W", "E"]:
            if default_rule not in self.include_rules:
                self.include_rules.extend([default_rule])

        for rule in self.all_rules.values():
            self.__register(rule)

    def __register(self, rule: CloudFormationLintRule):
        """Register and configure the rule"""
        if self.is_rule_enabled(rule):
            self.used_rules.add(rule.id)
            self.rules[rule.id] = rule
            rule.configure(
                self.configure_rules.get(rule.id, None), self.include_experimental
            )

    def register(self, rule: CloudFormationLintRule):
        """Register rules"""
        # Some rules are inheritited to limit code re-use.
        # These rules have no rule ID so we filter this out
        if rule.id != "":
            if rule.id in self.all_rules:
                raise DuplicateRuleError(rule_id=rule.id)
            self.all_rules[rule.id] = rule
            self.__register(rule)

    def __iter__(self):
        return iter(self.rules.values())

    def __len__(self):
        return len(self.rules.keys())

    def extend(self, more):
        """Extend rules"""
        for rule in more:
            self.register(rule)

    def __repr__(self):
        return "\n".join([self.rules[id].verbose() for id in sorted(self.rules)])

    def is_rule_enabled(self, rule: CloudFormationLintRule):
        """Checks if an individual rule is valid"""
        return rule.is_enabled(
            self.include_experimental,
            self.ignore_rules,
            self.include_rules,
            self.mandatory_rules,
        )

    # pylint: disable=inconsistent-return-statements
    def run_check(self, check, filename, rule_id, *args):
        """Run a check"""
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
                message = "Unknown exception while processing rule {}: {}"
                return [
                    Match(
                        1,
                        1,
                        1,
                        1,
                        filename,
                        RuleError(),
                        message.format(rule_id, error_message),
                    )
                ]

    def run(self, filename: Optional[str], cfn: Template):
        """Run rules"""
        matches = []
        for rule in self.rules.values():
            rule.initialize(cfn)

        for rule in self.rules.values():
            for key in rule.child_rules.keys():
                rule.child_rules[key] = self.rules.get(key)

        for rule in self.rules.values():
            matches.extend(
                self.run_check(rule.matchall, filename, rule.id, filename, cfn)
            )

        for resource_name, resource_attributes in cfn.get_resources().items():
            resource_type = resource_attributes.get("Type")
            resource_properties = resource_attributes.get("Properties")
            if isinstance(resource_type, str) and isinstance(resource_properties, dict):
                path = ["Resources", resource_name, "Properties"]
                for rule in self.rules.values():
                    matches.extend(
                        self.run_check(
                            rule.matchall_resource_properties,
                            filename,
                            rule.id,
                            filename,
                            cfn,
                            resource_properties,
                            resource_type,
                            path,
                        )
                    )

        return matches

    def create_from_module(self, modpath):
        """Create rules from a module import path"""
        mod = importlib.import_module(modpath)
        self.extend(cfnlint.helpers.create_rules(mod))

    def create_from_directory(self, rulesdir):
        """Create rules from directory"""
        result = []
        if rulesdir != "":
            result = cfnlint.helpers.load_plugins(os.path.expanduser(rulesdir))
        self.extend(result)

    def create_from_custom_rules_file(self, custom_rules_file):
        """Create rules from custom rules file"""
        custom_rules = []
        if custom_rules_file:
            with open(custom_rules_file, encoding="utf-8") as customRules:
                line_number = 1
                for line in customRules:
                    LOGGER.debug("Processing Custom Rule Line %d", line_number)
                    custom_rule = cfnlint.rules.custom.make_rule(line, line_number)
                    if custom_rule:
                        custom_rules.append(custom_rule)
                    line_number += 1

        self.extend(custom_rules)


<<<<<<< HEAD
class RuleMatch:
    """Rules Error"""

    def __init__(self, path, message, **kwargs):
        """Init"""
        self.path = path
        self.path_string = "/".join(map(str, path))
        self.message = message
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __eq__(self, item):
        """Override unique"""
        return (self.path, self.message) == (item.path, item.message)

    def __hash__(self):
        """Hash for comparisons"""
        return hash((self.path, self.message))
=======
class Match:  # pylint: disable=R0902
    """Match Classes"""

    def __init__(
        self,
        linenumber,
        columnnumber,
        linenumberend,
        columnnumberend,
        filename,
        rule,
        message=None,
        rulematch_obj=None,
    ):
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
        file_str = self.filename + ":" if self.filename else ""
        return f"[{self.rule}] ({self.message}) matched {file_str}{self.linenumber}"

    def __eq__(self, item):
        """Override equal to compare matches"""
        return (self.linenumber, self.columnnumber, self.rule.id, self.message) == (
            item.linenumber,
            item.columnnumber,
            item.rule.id,
            item.message,
        )
>>>>>>> 83f57c754 (Convert to using CloudFormation provider schemas)


class ParseError(CloudFormationLintRule):
    """Parse Lint Rule"""

    id = "E0000"
    shortdesc = "Parsing error found when parsing the template"
    description = "Checks for JSON/YAML formatting errors in your template"
    source_url = "https://github.com/aws-cloudformation/cfn-python-lint"
    tags = ["base"]


class TransformError(CloudFormationLintRule):
    """Transform Lint Rule"""

    id = "E0001"
    shortdesc = "Error found when transforming the template"
    description = "Errors found when performing transformation on the template"
    source_url = "https://github.com/aws-cloudformation/cfn-python-lint"
    tags = ["base", "transform"]


class RuleError(CloudFormationLintRule):
    """Rule processing Error"""

    id = "E0002"
    shortdesc = "Error processing rule on the template"
    description = "Errors found when processing a rule on the template"
    source_url = "https://github.com/aws-cloudformation/cfn-python-lint"
    tags = ["base", "rule"]
