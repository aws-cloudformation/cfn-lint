"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import logging
import os
import sys
from copy import deepcopy
from typing import Any, Iterator, Sequence

import cfnlint.formatters
import cfnlint.maintenance
from cfnlint.config import ConfigMixIn, configure_logging
from cfnlint.decode.decode import decode
from cfnlint.exceptions import (
    CfnLintExitException,
    InvalidRegionException,
    UnexpectedRuleException,
)
from cfnlint.helpers import REGIONS
from cfnlint.rules import Match, Rules
from cfnlint.rules.errors import ConfigError, ParseError, TransformError
from cfnlint.schema import PROVIDER_SCHEMA_MANAGER, patch
from cfnlint.template.template import Template

LOGGER = logging.getLogger(__name__)


def get_formatter(config: ConfigMixIn) -> cfnlint.formatters.BaseFormatter:
    """
    Get a formatter instance based on the specified configuration.

    Args:
        config (ConfigMixIn): The configuration object containing the format setting.

    Returns:
        cfnlint.formatters.BaseFormatter: A formatter instance based
        on the specified format.

    """
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
    """
    Runs a set of rules against a CloudFormation template.

    Attributes:
        config (ConfigMixIn): The configuration object containing
        settings for the template scan.
        cfn (Template): The CloudFormation template object.
        rules (Rules): The set of rules to be applied to the template.

    Methods:
        _dedup(matches: Iterator[Match]) -> Iterator[Match]:
            Deduplicate a sequence of matches.
        run() -> Iterator[Match]:
            Run the rules against the CloudFormation template and
            yield the resulting matches.
        check_metadata_directives(matches: Iterator[Match]) -> Iterator[Match]:
            Filter matches based on metadata directives in the template.

    """

    def __init__(
        self,
        filename: str | None,
        template: dict[str, Any],
        config: ConfigMixIn,
        rules: Rules,
    ) -> None:
        """
        Initialize a new TemplateRunner instance.

        Args:
            filename (str | None): The filename of the CloudFormation template.
            template (dict[str, Any]): The CloudFormation template as a dictionary.
            config (ConfigMixIn): The configuration object containing
            settings for the template scan.
            rules (Rules): The set of rules to be applied to the template.
        """
        self.config = deepcopy(config)
        self.config.set_template_args(template)
        self.cfn = Template(filename, template, self.config.regions)
        self.rules = rules

    def _dedup(self, matches: Iterator[Match]) -> Iterator[Match]:
        """
        Deduplicate a sequence of matches.

        Args:
            matches (Iterator[Match]): The sequence of matches to be deduplicated.

        Yields:
            Match: The unique matches from the input sequence.
        """
        seen: list[Match] = []
        for match in matches:
            if match not in seen:
                seen.append(match)
                yield match

    def run(self) -> Iterator[Match]:
        """
        Run the rules against the CloudFormation template and
        yield the resulting matches.

        Yields:
            Match: The matches found by running the rules against the template.
        """
        LOGGER.info("Run scan of template %s", self.cfn.filename)
        if not set(self.config.regions).issubset(set(REGIONS)):
            unsupported_regions = list(
                set(self.config.regions).difference(set(REGIONS))
            )
            raise InvalidRegionException(
                (
                    f"Regions {unsupported_regions!r} are unsupported. "
                    f"Supported regions are {REGIONS!r}"
                ),
                32,
            )

        matches = self.cfn.transform()
        if matches:
            if self.rules.is_rule_enabled(TransformError(), self.config):
                yield from iter(matches)
            return

        if self.cfn.template is not None:
            if self.config.build_graph:
                self.cfn.build_graph()
            yield from self._dedup(
                self.check_metadata_directives(
                    self.rules.run(
                        filename=self.cfn.filename, cfn=self.cfn, config=self.config
                    )
                )
            )

    def check_metadata_directives(self, matches: Iterator[Match]) -> Iterator[Match]:
        """
        Filter matches based on metadata directives in the template.

        Args:
            matches (Iterator[Match]): The sequence of matches to be filtered.

        Yields:
            Match: The matches that are not suppressed by metadata directives.
        """
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
                    path = getattr(match, "path", None)
                    if path:
                        if len(path) >= 2:
                            if path[0] != "Resources":
                                yield match
                                continue
                            if path[1] not in directives[match.rule.id]:
                                yield match
                        else:
                            yield match


class Runner:
    """
    Runs a set of rules against one or more CloudFormation templates.

    Attributes:
        config (ConfigMixIn): The configuration object containing
        settings for the template scan.
        formatter (BaseFormatter): The formatter used to output the
        results of the template scan.
        rules (Rules): The set of rules to be applied to the templates.

    Methods:
        _get_rules() -> None:
            Load the rules to be applied to the templates.
        _validate_filenames(filenames: Sequence[str | None]) -> Iterator[Match]:
            Validate the specified filenames and yield any matches found.
        validate_template(filename: str | None,
         template: dict[str, Any]) -> Iterator[Match]:
            Validate a single CloudFormation template and yield any matches found.
        _cli_output(matches: list[Match]) -> None:
            Output the results of the template scan to the console or a file.
        _exit(matches: list[Match]) -> int:
            Determine the appropriate exit code based on the severity of the matches.
        run() -> Iterator[Match]:
            Run the template validation process and yield any matches found.
        cli() -> None:
            Run the template validation process and output the results.
    """

    def __init__(self, config: ConfigMixIn) -> None:
        """
        Initialize a new Runner instance.

        Args:
            config (ConfigMixIn): The configuration object containing
                settings for the template scan.
        """
        self.config = config
        self.formatter = get_formatter(self.config)
        self.rules: Rules = Rules()
        self._get_rules()
        try:
            self.config.templates
        except ValueError as e:
            self._cli_output([Match(str(e), ConfigError(), None)])
        # load registry schemas before patching
        if self.config.registry_schemas:
            for path in self.config.registry_schemas:
                PROVIDER_SCHEMA_MANAGER.load_registry_schemas(path)
        # now we can patch after loading all registry schemas
        if self.config.override_spec:
            patch(self.config.override_spec, self.config.regions)

    def _get_rules(self) -> None:
        """
        Load the rules to be applied to the templates.
        """
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
        """
        Validate the specified filenames and yield any matches found.

        This function processes each filename in the provided sequence, decoding the
        template and validating it against the configured rules. Any matches found
        are yielded as an iterator.

        Args:
            filenames (Sequence[str | None]): The sequence of filenames to be validated.

        Yields:
            Match: The matches found during the validation process.

        Raises:
            None: This function does not raise any exceptions.
        """
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
                if ignore_bad_template or any(
                    "E0000".startswith(x) for x in self.config.ignore_checks
                ):
                    matches = [match for match in matches if match.rule.id != "E0000"]

                yield from iter(matches)
                continue
            yield from self.validate_template(filename, template)  # type: ignore[arg-type] # noqa: E501

    def validate_template(
        self, filename: str | None, template: dict[str, Any]
    ) -> Iterator[Match]:
        """
        Validate a single CloudFormation template and yield any matches found.

        This function takes a CloudFormation template as a dictionary and runs the
        configured rules against it. Any matches found are yielded as an iterator.

        Args:
            filename (str | None): The filename of the CloudFormation template, or
                `None` if the template is not associated with a file.
            template (dict[str, Any]): The CloudFormation template as a dictionary.

        Yields:
            Match: The matches found during the validation process.

        Raises:
            None: This function does not raise any exceptions.
        """
        runner = TemplateRunner(filename, template, self.config, self.rules)
        yield from runner.run()

    def _cli_output(self, matches: list[Match]) -> None:
        formatter = get_formatter(self.config)
        matches.sort(key=lambda x: (x.filename, x.linenumber, x.rule.id))
        output = formatter.print_matches(matches, self.rules, config=self.config)
        if output:
            if self.config.output_file:
                with open(self.config.output_file, "w") as output_file:
                    output_file.write(output)
            else:
                print(output)

        self._exit(matches)

    def _exit(self, matches: list[Match]) -> int:
        """Determine exit code"""

        exit_level: str = self.config.non_zero_exit_code or "informational"

        exit_levels: dict[str, list[str]] = {
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
        """
        Run the rules against the CloudFormation template and yield
        the resulting matches.

        This function is responsible for executing the validation
        process against the CloudFormation template. It performs
        the following steps:

        1. Transform the template, if necessary, and yield any matches found.
        2. Build the template graph, if configured.
        3. Run the configured rules against the template and
        yield the resulting matches.
        4. Filter the matches based on any metadata directives in the template.
        5. Deduplicate the matches before yielding them.

        Yields:
            Match: The matches found by running the rules against the template.

        Raises:
            None: This function does not raise any exceptions.
        """

        if (not sys.stdin.isatty()) and (not self.config.templates_to_process):
            yield from self._validate_filenames([None])
            return

        yield from self._validate_filenames(self.config.templates)

    def cli(self) -> None:
        """
        Run the template validation process and output the results.

        This function is the entry point for the command-line interface (CLI) of the
        CloudFormation linter.

        If no templates are specified and the input is a terminal, the function will
        print the usage information and exit with a non-zero status code.

        Returns:
            None: This function does not return a value.

        Raises:
            None: This function does not raise any exceptions.
        """
        # Add our logging configuration when running CLI
        configure_logging(self.config.debug, self.config.info)

        if self.config.update_specs:
            cfnlint.maintenance.update_resource_specs(self.config.force)
            sys.exit(0)

        if self.config.patch_specs:
            cfnlint.maintenance.patch_resource_specs()
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

        if not self.config.templates_to_process:
            if sys.stdin.isatty():
                self.config.parser.print_help()
                sys.exit(1)

        try:
            self._cli_output(list(self.run()))
        except CfnLintExitException as e:
            LOGGER.error(str(e))
            sys.exit(e.exit_code)


def main() -> None:
    try:
        config = ConfigMixIn(sys.argv[1:])
    except Exception as e:
        print(e)
        sys.exit(1)
    runner = Runner(config)
    runner.cli()
