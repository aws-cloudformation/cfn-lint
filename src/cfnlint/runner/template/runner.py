"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import logging
from typing import Any, Iterator

from cfnlint.config import ConfigMixIn
from cfnlint.decode import decode
from cfnlint.helpers import REGIONS
from cfnlint.rules import Match, Rules
from cfnlint.rules.errors import TransformError
from cfnlint.runner.exceptions import InvalidRegionException
from cfnlint.template.template import Template

LOGGER = logging.getLogger(__name__)


def _dedup(matches: Iterator[Match]) -> Iterator[Match]:
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


def _check_metadata_directives(
    matches: Iterator[Match], cfn: Template, config: ConfigMixIn
) -> Iterator[Match]:
    """
    Filter matches based on metadata directives in the template.

    Args:
        matches (Iterator[Match]): The sequence of matches to be filtered.

    Yields:
        Match: The matches that are not suppressed by metadata directives.
    """
    directives = cfn.get_directives()

    for match in matches:
        if match.rule.id not in directives:
            yield match
        else:
            for mandatory_check in config.mandatory_checks:
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


def _run_template_per_config(
    cfn: Template, config: ConfigMixIn, rules: Rules
) -> Iterator[Match]:

    LOGGER.info("Run scan of template %s", cfn.filename)
    if not set(config.regions).issubset(set(REGIONS)):
        unsupported_regions = list(set(config.regions).difference(set(REGIONS)))
        raise InvalidRegionException(
            (
                f"Regions {unsupported_regions!r} are unsupported. "
                f"Supported regions are {REGIONS!r}"
            ),
            32,
        )

    matches = cfn.transform()
    if matches:
        if rules.is_rule_enabled(TransformError(), config):
            yield from iter(matches)
        return

    if cfn.template is not None:
        if config.build_graph:
            cfn.build_graph()
        yield from _check_metadata_directives(
            rules.run(filename=cfn.filename, cfn=cfn, config=config),
            cfn=cfn,
            config=config,
        )


def _run_template(
    filename: str | None, template: Any, config: ConfigMixIn, rules: Rules
) -> Iterator[Match]:

    config.set_template_args(template)
    if config.parameters:
        matches: list[Match] = []
        for parameters in config.parameters:
            cfn = Template(filename, template, config.regions, parameters)
            matches.extend(list(_run_template_per_config(cfn, config, rules)))
        yield from _dedup(iter(matches))
    else:
        cfn = Template(filename, template, config.regions)
        yield from _dedup(_run_template_per_config(cfn, config, rules))


def run_template_by_file_path(
    filename: str | None, config: ConfigMixIn, rules: Rules, ignore_bad_template: bool
) -> Iterator[Match]:
    """
    Runs a set of rules against a CloudFormation template.

    Attributes:
        config (ConfigMixIn): The configuration object containing
        settings for the template scan.
        cfn (Template): The CloudFormation template object.
        rules (Rules): The set of rules to be applied to the template.
    """

    (template, matches) = decode(filename)  # type: ignore
    if matches:
        if ignore_bad_template or any(
            "E0000".startswith(x) for x in config.ignore_checks
        ):
            matches = [match for match in matches if match.rule.id != "E0000"]

        yield from iter(matches)
        return
    yield from _run_template(filename, template, config, rules)


def run_template_by_data(
    template: dict[str, Any], config: ConfigMixIn, rules: Rules
) -> Iterator[Match]:
    """
    Runs a set of rules against a CloudFormation template.

    Attributes:
        config (ConfigMixIn): The configuration object containing
        settings for the template scan.
        cfn (Template): The CloudFormation template object.
        rules (Rules): The set of rules to be applied to the template.
    """

    yield from _run_template(None, template, config, rules)
