"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import logging
import sys
import os
from typing import List, Optional, Sequence, Union
from cfnlint.rules import (
    Match,
    ParseError,
    Rules,
    TransformError,
)
import cfnlint.formatters
import cfnlint.maintenance
from cfnlint.config import ConfigMixIn
from cfnlint.rules import Match, Rules
from cfnlint.template.template import Template

LOGGER = logging.getLogger(__name__)
_DEFAULT_RULESDIR = os.path.join(os.path.dirname(__file__), "rules")


def get_formatter(config: ConfigMixIn) -> cfnlint.formatters.BaseFormatter:
    fmt = config.format
    if fmt:
        if fmt == "quiet":
            return cfnlint.formatters.QuietFormatter()
        if fmt == "parseable":
            # pylint: disable=bad-option-value
            return cfnlint.formatters.ParseableFormatter()
        if fmt == "json":
            return cfnlint.formatters.JsonFormatter()
        if fmt == "junit":
            return cfnlint.formatters.JUnitFormatter()
        if fmt == "pretty":
            return cfnlint.formatters.PrettyFormatter()
        if fmt == "sarif":
            return cfnlint.formatters.SARIFFormatter()

    return cfnlint.formatters.Formatter()


class Runner:
    def __init__(self, config: ConfigMixIn) -> None:
        self.config = config
        self.formatter = get_formatter(self.config)
        self.rules = Rules()

    def _get_rules(self):
        self.rules = Rules()
        rules_paths: List[str] = [_DEFAULT_RULESDIR] + self.config.append_rules
        try:
            for rules_path in rules_paths:
                if rules_path and os.path.isdir(os.path.expanduser(rules_path)):
                    self.rules += Rules.create_from_directory(rules_path)
                else:
                    self.rules += Rules.create_from_module(rules_path)

            self.rules += Rules.create_from_custom_rules_file(self.config.custom_rules)
        except (OSError, ImportError) as e:
            raise UnexpectedRuleException(
                f"Tried to append rules but got an error: {str(e)}", 1
            ) from e

    def run(self) -> None:
        formatter = get_formatter(self.config)

        if self.config.update_specs:
            cfnlint.maintenance.update_resource_specs(self.config.force)
            sys.exit(0)

        if self.config.update_iam_policies:
            cfnlint.maintenance.update_iam_policies()
            sys.exit(0)

        # Remaining actions need rules
        self._get_rules()

        if self.config.update_documentation:
            # Get ALL rules (ignore the CLI settings))
            cfnlint.maintenance.update_documentation(self.rules)
            sys.exit(0)

        if self.config.listrules:
            print(self.rules)
            sys.exit(0)

        if not sys.stdin.isatty() and not self.config.templates:
            return (self.config, [None], formatter)

        if not self.config.templates:
            # Not specified, print the help
            self.config.parser.print_help()
            sys.exit(1)

        return (self.config, formatter)


def main() -> None:
    config = ConfigMixIn(sys.argv[1:])
    runner = Runner(config)
    runner.run()


class LegacyRunner:
    """Run all the rules"""

    def __init__(
        self,
        rules: Rules,
        filename: Optional[str],
        template: str,
        regions: Sequence[str],
        verbosity=0,
        mandatory_rules: Union[Sequence[str], None] = None,
    ):
        self.rules = rules
        self.filename = filename
        self.verbosity = verbosity
        self.mandatory_rules = mandatory_rules or []
        self.cfn = Template(filename, template, regions)

    def transform(self):
        """Transform logic"""
        matches = self.cfn.transform()
        return matches

    def run(self) -> List[Match]:
        """Run rules"""
        LOGGER.info("Run scan of template %s", self.filename)
        matches = []
        if self.cfn.template is not None:
            matches.extend(self.rules.run(self.filename, self.cfn))
        return self.check_metadata_directives(matches)

    def check_metadata_directives(self, matches: Sequence[Match]) -> List[Match]:
        # uniq the list of incidents and filter out exceptions from the template
        directives = self.cfn.get_directives()
        return_matches: List[Match] = []

        for check in self.rules.ignore_rules:
            print(check)
        for match in matches:
            if not any(match == u for u in return_matches):
                if match.rule.id not in directives:
                    return_matches.append(match)
                else:
                    for mandatory_rule in self.mandatory_rules:
                        if match.rule.id.startswith(mandatory_rule):
                            return_matches.append(match)
                            break
                    else:
                        for directive in directives.get(match.rule.id):
                            start = directive.get("start")
                            end = directive.get("end")
                            if start[0] < match.linenumber < end[0]:
                                break
                            if (
                                start[0] == match.linenumber
                                and start[1] <= match.columnnumber
                            ):
                                break
                            if (
                                end[0] == match.linenumber
                                and end[1] >= match.columnnumberend
                            ):
                                break
                        else:
                            return_matches.append(match)

        return return_matches


class CfnLintExitException(Exception):
    """Generic exception used when the cli should exit"""

    def __init__(self, msg=None, exit_code=1):
        if msg is None:
            msg = f"process failed with exit code {exit_code}"
        super().__init__(msg)
        self.exit_code = exit_code


class InvalidRegionException(CfnLintExitException):
    """When an unsupported/invalid region is supplied"""


class UnexpectedRuleException(CfnLintExitException):
    """When processing a rule fails in an unexpected way"""
