"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.testlib.testcase import BaseTestCase

import cfnlint.core
import cfnlint.helpers  # pylint: disable=E0401


class TestGetTemplateRules(BaseTestCase):
    """
    Validate that the rule configuration is being reset
    Rules are cached between rules for speed so they need
    to be reconfigured between runs
    """

    def test_invalid_rule(self):
        """test invalid rules"""
        filename = "test/fixtures/templates/bad/core/config_configure_e3012.yaml"
        (args, _, _) = cfnlint.core.get_args_filenames(
            [
                "--template",
                filename,
            ]
        )

        (_, rules, errors) = cfnlint.core.get_template_rules(filename, args)

        self.assertEqual(len(errors), 0)
        for rule in rules:
            if rule.id == "E3012":
                self.assertEqual(rule.config, {"strict": True})

        filename = "test/fixtures/templates/good/core/config_default_e3012.yaml"
        (args, _, _) = cfnlint.core.get_args_filenames(
            [
                "--template",
                filename,
            ]
        )

        (_, rules, errors) = cfnlint.core.get_template_rules(filename, args)
        self.assertEqual(len(errors), 0)
        for rule in rules:
            if rule.id == "E3012":
                self.assertEqual(rule.config, {"strict": False})
