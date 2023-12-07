"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import logging
import os
import sys
from copy import deepcopy
from typing import Dict, List, Sequence

import cfnlint.formatters
import cfnlint.maintenance
from cfnlint.config import ConfigMixIn
from cfnlint.decode.decode import decode
from cfnlint.rules import Iterator, Match, ParseError, Rules, TransformError
from cfnlint.schema import PROVIDER_SCHEMA_MANAGER
from cfnlint.template.template import Template

LOGGER = logging.getLogger(__name__)


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


class TemplateRunner:
    def __init__(
        self, filename: str | None, template: str, config: ConfigMixIn, rules: Rules
    ) -> None:
        self.cfn = Template(filename, template, config.regions)
        self.rules = rules
        self.config = deepcopy(config)
        self.config.template_args = template

    def _dedup(self, matches: Iterator[Match]) -> Iterator[Match]:
        """Deduplicate matches"""
        seen: List[Match] = []
        for match in matches:
            if match not in seen:
                seen.append(match)
                yield match

    def run(self) -> Iterator[Match]:
        """Run rules"""
        LOGGER.info("Run scan of template %s", self.cfn.filename)
        matches = self.cfn.transform()
        if matches:
            # Transform logic helps with handling serverless templates
            if self.rules.is_rule_enabled(
                TransformError(),
                self.config,
            ):
                yield from iter(matches)
            return
        if self.cfn.template is not None:
            yield from self._dedup(
                self.check_metadata_directives(
                    self.rules.run(
                        filename=self.cfn.filename, cfn=self.cfn, config=self.config
                    )
                )
            )

    def check_metadata_directives(self, matches: Iterator[Match]) -> Iterator[Match]:
        # uniq the list of incidents and filter out exceptions from the template
        directives = self.cfn.get_directives()

        for match in matches:
            if match.rule.id not in directives:
                yield match
            else:
                for mandatory_check in self.config.mandatory_checks:
                    if match.rule.id.startswith(mandatory_check):
                        yield match
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
                        yield match


class Runner:
    def __init__(self, config: ConfigMixIn) -> None:
        self.config = config
        self.formatter = get_formatter(self.config)
        self.rules: Rules = Rules()
        self._get_rules()
        if self.config.override_spec:
            PROVIDER_SCHEMA_MANAGER.patch(
                self.config.override_spec, self.config.regions
            )
        if self.config.registry_schemas:
            for path in self.config.registry_schemas:
                PROVIDER_SCHEMA_MANAGER.load_registry_schemas(path)

    def _get_rules(self):
        self.rules = Rules()
        try:
            for rules_path in self.config.append_rules:
                if rules_path and os.path.isdir(os.path.expanduser(rules_path)):
                    self.rules.update(Rules.create_from_directory(rules_path))
                else:
                    self.rules.update(Rules.create_from_module(rules_path))

            self.rules.update(
                Rules.create_from_custom_rules_file(self.config.custom_rules)
            )
        except (OSError, ImportError) as e:
            raise UnexpectedRuleException(
                f"Tried to append rules but got an error: {str(e)}", 1
            ) from e

    def _validate_filenames(self, filenames: Sequence[str | None]) -> Iterator[Match]:
        ignore_bad_template: bool = False
        if self.config.ignore_bad_template:
            ignore_bad_template = True
        else:
            # There is no collection at this point so we need to handle this
            # check directly
            if not ParseError().is_enabled(
                include_experimental=False,
                ignore_rules=self.config.ignore_checks,
                include_rules=self.config.include_checks,
                mandatory_rules=self.config.mandatory_checks,
            ):
                ignore_bad_template = True
        for filename in filenames:
            (template, matches) = decode(filename)
            if matches:
                if not (
                    len(matches) == 1
                    and ignore_bad_template
                    and matches[0].rule.id == "E0000"
                ):
                    yield from iter(matches)
                    continue
            yield from self.validate_template(filename, template)  # type: ignore[arg-type] # noqa: E501

    def validate_template(self, filename: str | None, template: str) -> Iterator[Match]:
        runner = TemplateRunner(filename, template, self.config, self.rules)
        yield from runner.run()

    def _cli_output(self, matches: List[Match]) -> None:
        formatter = get_formatter(self.config)
        output = formatter.print_matches(list(matches), self.rules, config=self.config)
        if output:
            if self.config.output_file:
                with open(self.config.output_file, "w") as output_file:
                    output_file.write(output)
            else:
                print(output)

        self._exit(matches)

    def _exit(self, matches: List[Match]) -> int:
        """Determine exit code"""

        exit_level: str = self.config.non_zero_exit_code or "informational"

        exit_levels: Dict[str, List[str]] = {
            "informational": ["informational", "warning", "error"],
            "warning": ["warning", "error"],
            "error": ["error"],
            "none": [],
        }

        exit_code = 0
        for match in matches:
            if (
                match.rule.severity == "informational"
                and match.rule.severity in exit_levels[exit_level]
            ):
                exit_code = exit_code | 8
            elif (
                match.rule.severity == "warning"
                and match.rule.severity in exit_levels[exit_level]
            ):
                exit_code = exit_code | 4
            elif (
                match.rule.severity == "error"
                and match.rule.severity in exit_levels[exit_level]
            ):
                exit_code = exit_code | 2

        sys.exit(exit_code)

    def run(self) -> Iterator[Match]:
        if not sys.stdin.isatty() and not self.config.templates:
            yield from self._validate_filenames([None])
            return

        yield from self._validate_filenames(self.config.templates)

    def cli(self) -> None:
        if self.config.update_specs:
            cfnlint.maintenance.update_resource_specs(self.config.force)
            sys.exit(0)

        if self.config.update_iam_policies:
            cfnlint.maintenance.update_iam_policies()
            sys.exit(0)

        if self.config.update_documentation:
            # Get ALL rules (ignore the CLI settings))
            cfnlint.maintenance.update_documentation(self.rules)
            sys.exit(0)

        if self.config.listrules:
            print(self.rules)
            sys.exit(0)

        if not self.config.templates:
            if sys.stdin.isatty():
                self.config.parser.print_help()
                sys.exit(1)

        self._cli_output(list(self.run()))


def main() -> None:
    config = ConfigMixIn(sys.argv[1:])
    runner = Runner(config)
    runner.cli()


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
