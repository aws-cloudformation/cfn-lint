"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import logging
from copy import deepcopy
from typing import Any, Iterator

from cfnlint.config import ConfigMixIn
from cfnlint.helpers import REGIONS
from cfnlint.rules import Match, Rules
from cfnlint.rules.errors import TransformError
from cfnlint.runner.exceptions import InvalidRegionException
from cfnlint.template.template import Template

LOGGER = logging.getLogger(__name__)


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
