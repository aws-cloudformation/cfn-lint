"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import importlib
import logging
import os
import traceback
from collections import UserDict
from typing import TYPE_CHECKING, Any, Callable, Iterator, MutableSet

import cfnlint.helpers
import cfnlint.rules.custom
from cfnlint.exceptions import DuplicateRuleError
from cfnlint.rules._rule import CloudFormationLintRule, Match
from cfnlint.rules.errors import RuleError
from cfnlint.template import Template

if TYPE_CHECKING:
    from cfnlint.config import ConfigMixIn

    TypedRules = UserDict[str, "CloudFormationLintRule"]
else:
    TypedRules = UserDict


LOGGER = logging.getLogger(__name__)


class Rules(TypedRules):
    def __init__(
        self, rules: dict[str, CloudFormationLintRule] | None = None, /, **kwargs
    ):
        super().__init__()
        self.data: dict[str, CloudFormationLintRule] = {}
        self._used_rules: dict[str, CloudFormationLintRule] = {}
        if rules is not None:
            self.update(rules)
        if kwargs:
            self.update(kwargs)

    def __repr__(self):
        return "\n".join([self.data[id].verbose() for id in sorted(self.data)])

    def __delitem__(self, i: str) -> None:
        raise RuntimeError("Deletion is not allowed")

    def __setitem__(self, key: str, item: CloudFormationLintRule) -> None:
        if not key:
            return
        if key in self.data:
            raise DuplicateRuleError(rule_id=key)
        return super().__setitem__(key, item)

    def register(self, rule: CloudFormationLintRule) -> None:
        self[rule.id] = rule

    def filter(
        self,
        func: Callable[[dict[str, CloudFormationLintRule], ConfigMixIn], Rules],
        config: ConfigMixIn,
    ):
        return func(self.data, config)

    def is_rule_enabled(
        self, rule: str | CloudFormationLintRule, config: ConfigMixIn
    ) -> bool:
        if isinstance(rule, str):
            if rule not in self.data:
                return False
            rule = self.data[rule]
        if rule.is_enabled(
            include_experimental=config.include_experimental,
            ignore_rules=config.ignore_checks,
            include_rules=config.include_checks,
            mandatory_rules=config.mandatory_checks,
        ):
            return True
        return False

    def extend(self, rules: list[CloudFormationLintRule]):
        for rule in rules:
            self.register(rule)

    @property
    def used_rules(self) -> dict[str, CloudFormationLintRule]:
        return self._used_rules

    # pylint: disable=inconsistent-return-statements
    def run_check(self, check, filename, rule_id, config, *args) -> Iterator[Match]:
        """Run a check"""
        if self.is_rule_enabled(rule_id, config):
            self._used_rules[rule_id] = self.data[rule_id]
        try:
            yield from iter(check(*args))
        except Exception as err:  # pylint: disable=W0703
            if self.is_rule_enabled(RuleError(), config):
                # In debug mode, print the error include complete stack trace
                if LOGGER.getEffectiveLevel() == logging.DEBUG:
                    error_message = traceback.format_exc()
                else:
                    error_message = str(err)
                yield Match.create(
                    filename=filename,
                    rule=RuleError(),
                    message=(
                        "Unknown exception while processing "
                        f"rule {rule_id}: {error_message!r}"
                    ),
                )

    def _filter_matches(
        self, config: ConfigMixIn, matches: Iterator[Match]
    ) -> Iterator[Match]:
        """Filter matches by config"""
        for match in matches:
            if self.is_rule_enabled(match.rule, config):
                yield match

    def run(
        self, filename: str | None, cfn: Template, config: ConfigMixIn
    ) -> Iterator[Match]:
        """Run rules"""
        for rule_id, rule in self.data.items():
            rule.configure(
                config.configure_rules.get(rule_id, None), config.include_experimental
            )
            rule.initialize(cfn)

        for rule_id, rule in self.data.items():
            for key in rule.child_rules.keys():
                if not any(key == r for r in self.data.keys()):
                    continue
                rule.child_rules[key] = self.data.get(key)
            for parent_rule in rule.parent_rules:
                if parent_rule in self.data:
                    self.data[parent_rule].child_rules[rule_id] = rule

        for rule_id, rule in self.data.items():
            yield from self._filter_matches(
                config,
                self.run_check(rule.matchall, filename, rule_id, config, filename, cfn),
            )

        for resource_name, resource_attributes in cfn.get_resources().items():
            resource_type = resource_attributes.get("Type")
            resource_properties = resource_attributes.get("Properties")
            if isinstance(resource_type, str) and isinstance(resource_properties, dict):
                path = ["Resources", resource_name, "Properties"]
                for rule_id, rule in self.data.items():
                    yield from self._filter_matches(
                        config,
                        self.run_check(
                            rule.matchall_resource_properties,
                            filename,
                            rule_id,
                            config,
                            filename,
                            cfn,
                            resource_properties,
                            resource_type,
                            path,
                        ),
                    )

    @classmethod
    def _from_list(cls, items: list[CloudFormationLintRule]) -> Rules:
        rules = Rules()
        for item in items:
            rules[item.id] = item

        return rules

    @classmethod
    def create_from_module(cls, modpath: str) -> Rules:
        """Create rules from a module import path"""
        mod = importlib.import_module(modpath)
        return cls._from_list(cfnlint.helpers.create_rules(mod))

    @classmethod
    def create_from_directory(cls, rulesdir: str) -> Rules:
        if rulesdir != "":
            return cls._from_list(
                cfnlint.helpers.load_plugins(os.path.expanduser(rulesdir))
            )

        return cls({})

    @classmethod
    def create_from_custom_rules_file(cls, custom_rules_file) -> Rules:
        """Create rules from custom rules file"""
        custom_rules = cls({})
        if custom_rules_file:
            with open(custom_rules_file, encoding="utf-8") as customRules:
                line_number = 1
                for line in customRules:
                    LOGGER.debug("Processing Custom Rule Line %d", line_number)
                    custom_rule = cfnlint.rules.custom.make_rule(line, line_number)
                    if custom_rule:
                        custom_rules[custom_rule.id] = custom_rule
                    line_number += 1

        return custom_rules


# pylint: disable=too-many-instance-attributes
class RulesCollection:
    """Collection of rules"""

    def __init__(
        self,
        ignore_rules: list[str] | None = None,
        include_rules: list[str] | None = None,
        configure_rules: Any = None,
        include_experimental: bool = False,
        mandatory_rules: list[str] | None = None,
    ):
        self.rules: dict[str, CloudFormationLintRule] = {}
        self.all_rules: dict[str, CloudFormationLintRule] = {}
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
        ignore_rules: list[str] | None = None,
        include_rules: list[str] | None = None,
        configure_rules: Any = None,
        include_experimental: bool = False,
        mandatory_rules: list[str] | None = None,
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
        if self.is_rule_enabled(rule) or rule.child_rules:
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
            matches = []
            for match in check(*args):
                if self.is_rule_enabled(match.rule):
                    matches.append(match)
            return matches
        except Exception as err:  # pylint: disable=W0703
            if self.is_rule_enabled(RuleError()):
                # In debug mode, print the error include complete stack trace
                if LOGGER.getEffectiveLevel() == logging.DEBUG:
                    error_message = traceback.format_exc()
                else:
                    error_message = str(err)
                message = "Unknown exception while processing rule {}: {}"
                return [
                    Match.create(
                        filename=filename,
                        rule=RuleError(),
                        message=message.format(rule_id, error_message),
                    )
                ]

        return []

    def run(self, filename: str | None, cfn: Template, config=None):
        """Run rules"""
        matches = []
        for rule in self.rules.values():
            rule.initialize(cfn)

        for rule in self.rules.values():
            for key in rule.child_rules.keys():
                rule.child_rules[key] = self.rules.get(key)
            for parent_rule in rule.parent_rules:
                if parent_rule in self.rules:
                    self.rules[parent_rule].child_rules[rule.id] = rule

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
