"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import os
from typing import List, Union

from cfnlint.config import _DEFAULT_RULESDIR
from cfnlint.rules import RulesCollection
from cfnlint.runner import UnexpectedRuleException


def get_rules(
    append_rules: List[str],
    ignore_rules: List[str],
    include_rules: List[str],
    configure_rules=None,
    include_experimental: bool = False,
    mandatory_rules: Union[List[str], None] = None,
    custom_rules: Union[str, None] = None,
) -> RulesCollection:
    rules = RulesCollection(
        ignore_rules,
        include_rules,
        configure_rules,
        include_experimental,
        mandatory_rules,
    )
    rules_paths: List[str] = [_DEFAULT_RULESDIR] + append_rules
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
