"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import logging
from typing import Any, Iterator

from cfnlint.config import ConfigMixIn
from cfnlint.decode import decode
from cfnlint.exceptions import InvalidRegionException
from cfnlint.helpers import REGIONS
from cfnlint.rules import Match, Rules
from cfnlint.rules.errors import ParseError, TransformError
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

    if not isinstance(template, dict):
        # pylint: disable=import-outside-toplevel
        from cfnlint.rules.errors import ParseError

        # Template isn't a dict which means nearly nothing will work
        yield Match.create(
            filename=filename or "",
            rule=ParseError(),
            message="Template needs to be an object.",
        )

        return

    config.set_template_args(template)
    cfn = Template(filename, template, config.regions, config.parameters)
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


def run_template_by_pipe(config: ConfigMixIn, rules: Rules) -> Iterator[Match]:
    """
    Runs a set of rules against a CloudFormation template.

    Attributes:
        config (ConfigMixIn): The configuration object containing
        settings for the template scan.
        cfn (Template): The CloudFormation template object.
        rules (Rules): The set of rules to be applied to the template.
    """

    (template, matches) = decode(None)  # type: ignore
    if matches:
        yield from iter(matches)
        return
    yield from run_template_by_data(template, config, rules)  # type: ignore


def run_template_by_file_paths(config: ConfigMixIn, rules: Rules) -> Iterator[Match]:
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
    if config.ignore_bad_template:
        ignore_bad_template = True
    else:
        # There is no collection at this point so we need to handle this
        # check directly
        if not ParseError().is_enabled(
            include_experimental=False,
            ignore_rules=config.ignore_checks,
            include_rules=config.include_checks,
            mandatory_rules=config.mandatory_checks,
        ):
            ignore_bad_template = True
    for filename in config.templates:
        yield from run_template_by_file_path(
            filename, config, rules, ignore_bad_template
        )
