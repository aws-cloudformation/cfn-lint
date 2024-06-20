"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import os
from typing import Sequence

from cfnlint.config import _DEFAULT_RULESDIR, ConfigMixIn, ManualArgs
from cfnlint.match import Match
from cfnlint.rules import RulesCollection
from cfnlint.runner import TemplateRunner, UnexpectedRuleException


def get_rules(
    append_rules: list[str],
    ignore_rules: list[str],
    include_rules: list[str],
    configure_rules=None,
    include_experimental: bool = False,
    mandatory_rules: list[str] | None = None,
    custom_rules: str | None = None,
) -> RulesCollection:
    rules = RulesCollection(
        ignore_rules,
        include_rules,
        configure_rules,
        include_experimental,
        mandatory_rules,
    )
    rules_paths: list[str] = [_DEFAULT_RULESDIR] + append_rules
    try:
        for rules_path in rules_paths:
            if rules_path and os.path.isdir(os.path.expanduser(rules_path)):
                rules.create_from_directory(rules_path)
            else:
                rules.create_from_module(rules_path)

        rules.create_from_custom_rules_file(custom_rules)
    except (OSError, ImportError) as e:
        raise UnexpectedRuleException(
            f"Tried to append rules but got an error: {str(e)}", 1
        ) from e
    return rules


def run_checks(
    filename: str,
    template: dict,
    rules: RulesCollection | None,
    regions: Sequence[str],
    mandatory_rules: Sequence[str] | None = None,
) -> list[Match]:
    """Run Checks and Custom Rules against the template"""

    config: ManualArgs = ManualArgs(
        regions=list(regions),
        mandatory_checks=list(mandatory_rules or []),
    )

    if not rules:
        return []

    config_mixin = ConfigMixIn(
        [],
        **config,
    )

    runner = TemplateRunner(
        filename=filename,
        template=template,
        rules=rules,  # type: ignore
        config=config_mixin,
    )

    return list(runner.run())
