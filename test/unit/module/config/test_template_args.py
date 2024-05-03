"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import logging
from test.testlib.testcase import BaseTestCase

import cfnlint.config  # pylint: disable=E0401

LOGGER = logging.getLogger("cfnlint")


class TestTempalteArgs(BaseTestCase):
    """Test ConfigParser Arguments"""

    def tearDown(self):
        """Setup"""
        for handler in LOGGER.handlers:
            LOGGER.removeHandler(handler)

    def test_template_args(self):
        """test template args"""
        config = cfnlint.config.TemplateArgs(
            {
                "Metadata": {
                    "cfn-lint": {
                        "config": {
                            "regions": ["us-east-1", "us-east-2"],
                            "ignore_checks": ["E2530"],
                            "configure_rules": {"E3012": {"strict": "false"}},
                        }
                    }
                }
            }
        )

        self.assertEqual(config.template_args["regions"], ["us-east-1", "us-east-2"])
        self.assertEqual(
            config.template_args["configure_rules"], {"E3012": {"strict": "false"}}
        )

    def test_template_args_failure_bad_format(self):
        """test template args"""
        config = cfnlint.config.TemplateArgs(
            {
                "Metadata": {
                    "cfn-lint": {
                        "config": {"configure_rules": [{"E3012": {"strict": "false"}}]}
                    }
                }
            }
        )

        self.assertEqual(config.template_args.get("configure_rules"), None)

    def test_template_args_failure_bad_value(self):
        """test template args"""
        config = cfnlint.config.TemplateArgs(
            {
                "Metadata": {
                    "cfn-lint": {
                        "config": {
                            "configure_rules": [{"E3012": {"bad_value": "false"}}]
                        }
                    }
                }
            }
        )

        self.assertEqual(config.template_args.get("configure_rules"), None)

    def test_template_args_failure_good_and_bad_value(self):
        """test template args"""
        config = cfnlint.config.TemplateArgs(
            {
                "Metadata": {
                    "cfn-lint": {
                        "config": {
                            "configure_rules": [
                                {
                                    "A1": {"strict": "false"},
                                    "E3012": {"strict": "false"},
                                    "Z1": {"strict": "false"},
                                }
                            ]
                        }
                    }
                }
            }
        )

        self.assertEqual(config.template_args.get("configure_rules"), None)

    def test_bad_template_structure(self):
        """test template args"""
        config = cfnlint.config.TemplateArgs([])

        self.assertEqual(config._template_args, {})

    def test_bad_config_structure(self):
        """test template args"""
        config = cfnlint.config.TemplateArgs({"Metadata": {"cfn-lint": {"config": []}}})

        self.assertEqual(config._template_args, {})
