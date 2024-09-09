"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import logging
import os
from pathlib import Path
from test.testlib.testcase import BaseTestCase
from unittest.mock import patch

import cfnlint.config  # pylint: disable=E0401
from cfnlint.helpers import REGIONS

LOGGER = logging.getLogger("cfnlint")


class TestConfigMixIn(BaseTestCase):
    """Test ConfigParser Arguments"""

    def tearDown(self):
        """Setup"""
        for handler in LOGGER.handlers:
            LOGGER.removeHandler(handler)

    @patch("cfnlint.config.ConfigFileArgs._read_config", create=True)
    def test_config_mix_in(self, yaml_mock):
        """Test mix in"""
        yaml_mock.side_effect = [
            {"include_checks": ["I", "I1111"], "regions": ["us-west-2"]},
            {},
        ]

        config = cfnlint.config.ConfigMixIn(["--regions", "us-west-1"])
        self.assertEqual(config.regions, ["us-west-1"])
        self.assertEqual(config.include_checks, ["W", "E", "I", "I1111"])

    @patch("cfnlint.config.ConfigFileArgs._read_config", create=True)
    def test_config_precedence(self, yaml_mock):
        """Test precedence in"""

        yaml_mock.side_effect = [
            {
                "include_checks": ["I"],
                "ignore_checks": ["E3001"],
                "regions": ["us-west-2"],
            },
            {},
        ]
        config = cfnlint.config.ConfigMixIn(["--include-checks", "I1234", "I4321"])
        config.template_args = {
            "Metadata": {
                "cfn-lint": {
                    "config": {"include_checks": ["I9876"], "ignore_checks": ["W3001"]}
                }
            }
        }
        # config files wins
        self.assertEqual(config.regions, ["us-west-2"])
        # CLI should win
        self.assertEqual(config.include_checks, ["W", "E", "I1234", "I4321"])
        # template file wins over config file
        self.assertEqual(config.ignore_checks, ["W3001"])

    @patch("cfnlint.config.ConfigFileArgs._read_config", create=True)
    def test_config_file_output(self, yaml_mock):
        """Test precedence in"""

        yaml_mock.side_effect = [{"output_file": "test_output.txt"}, {}]
        config = cfnlint.config.ConfigMixIn([])

        # Config file wins
        self.assertEqual(config.output_file, "test_output.txt")

    @patch("cfnlint.config.ConfigFileArgs._read_config", create=True)
    def test_config_file_output_mixin(self, yaml_mock):
        """Test precedence in"""

        yaml_mock.side_effect = [{"output_file": "test_output.txt"}, {}]
        config = cfnlint.config.ConfigMixIn(["--output-file", "test_output_2.txt"])

        # CLI args win
        self.assertEqual(config.output_file, "test_output_2.txt")

    @patch.dict(
        os.environ,
        {
            "HOME": os.environ.get("HOME", ""),
            "USERPROFILE": os.environ.get("USERPROFILE", ""),
            "HOMEPATH": os.environ.get("HOMEPATH", ""),
            "HOMEDRIVE": os.environ.get("HOMEDRIVE", ""),
        },
        clear=True,
    )
    @patch("cfnlint.config.ConfigFileArgs._read_config", create=True)
    def test_config_default_region(self, yaml_mock):
        """Test precedence in"""

        yaml_mock.side_effect = [{}, {}]
        config = cfnlint.config.ConfigMixIn([])

        # test defaults
        self.assertEqual(config.regions, ["us-east-1"])

    @patch.dict(
        os.environ,
        {
            "AWS_REGION": "us-west-2",
            "AWS_DEFAULT_REGION": "us-west-1",
            "HOME": os.environ.get("HOME", ""),
            "USERPROFILE": os.environ.get("USERPROFILE", ""),
            "HOMEPATH": os.environ.get("HOMEPATH", ""),
            "HOMEDRIVE": os.environ.get("HOMEDRIVE", ""),
        },
        clear=True,
    )
    @patch("cfnlint.config.ConfigFileArgs._read_config", create=True)
    def test_config_region_from_AWS_REGION_envvar(self, yaml_mock):
        """Test precedence in"""

        yaml_mock.side_effect = [{}, {}]
        config = cfnlint.config.ConfigMixIn([])

        # test defaults
        self.assertEqual(config.regions, ["us-west-2"])

    @patch.dict(
        os.environ,
        {
            "AWS_DEFAULT_REGION": "us-west-1",
            "HOME": os.environ.get("HOME", ""),
            "USERPROFILE": os.environ.get("USERPROFILE", ""),
            "HOMEPATH": os.environ.get("HOMEPATH", ""),
            "HOMEDRIVE": os.environ.get("HOMEDRIVE", ""),
        },
        clear=True,
    )
    @patch("cfnlint.config.ConfigFileArgs._read_config", create=True)
    def test_config_region_from_AWS_DEFAULT_REGION_envvar(self, yaml_mock):
        """Test precedence in"""

        yaml_mock.side_effect = [{}, {}]
        config = cfnlint.config.ConfigMixIn([])

        # test defaults
        self.assertEqual(config.regions, ["us-west-1"])

    @patch("cfnlint.config.ConfigFileArgs._read_config", create=True)
    def test_config_all_regions(self, yaml_mock):
        """Test precedence in"""

        yaml_mock.side_effect = [{"regions": ["ALL_REGIONS"]}, {}]
        config = cfnlint.config.ConfigMixIn([])

        # test defaults
        self.assertEqual(config.regions, REGIONS)

    @patch("cfnlint.config.ConfigFileArgs._read_config", create=True)
    def test_config_force_with_update_specs(self, yaml_mock):
        """Test precedence in"""

        yaml_mock.side_effect = [{}, {}]
        config = cfnlint.config.ConfigMixIn(["--update-specs", "--force"])

        # test defaults
        self.assertEqual(config.force, True)
        self.assertEqual(config.update_specs, True)

    @patch("cfnlint.config.ConfigFileArgs._read_config", create=True)
    def test_config_expand_paths(self, yaml_mock):
        """Test precedence in"""

        yaml_mock.side_effect = [
            {"templates": ["test/fixtures/templates/public/*.yaml"]},
            {},
        ]
        config = cfnlint.config.ConfigMixIn([])

        # test defaults
        self.assertEqual(
            config.templates,
            [
                str(
                    Path(
                        "test/fixtures/templates/public"
                        + os.path.sep
                        + "lambda-poller.yaml"
                    )
                ),
                str(
                    Path(
                        "test/fixtures/templates/public"
                        + os.path.sep
                        + "rds-cluster.yaml"
                    )
                ),
            ],
        )

    @patch("cfnlint.config.ConfigFileArgs._read_config", create=True)
    def test_config_expand_paths_nomatch(self, yaml_mock):
        """Test precedence in"""

        filename = "test/fixtures/templates/nonexistant/*.yaml"
        yaml_mock.side_effect = [
            {"templates": [filename]},
            {},
        ]
        config = cfnlint.config.ConfigMixIn([])

        # test defaults
        self.assertEqual(config.templates, [])

    @patch("cfnlint.config.ConfigFileArgs._read_config", create=True)
    def test_config_expand_ignore_templates(self, yaml_mock):
        """Test ignore templates"""

        yaml_mock.side_effect = [
            {
                "templates": ["test/fixtures/templates/bad/resources/iam/*.yaml"],
                "ignore_templates": [
                    "test/fixtures/templates/bad/resources/iam/resource_*.yaml"
                ],
            },
            {},
        ]
        config = cfnlint.config.ConfigMixIn([])

        # test defaults
        self.assertNotIn(
            str(Path("test/fixtures/templates/bad/resources/iam/resource_policy.yaml")),
            config.templates,
        )
        self.assertEqual(len(config.templates), 3)

    @patch("cfnlint.config.ConfigFileArgs._read_config", create=True)
    def test_config_merge(self, yaml_mock):
        """Test merging lists"""

        yaml_mock.side_effect = [
            {
                "include_checks": ["I"],
                "ignore_checks": ["E3001"],
                "regions": ["us-west-2"],
            },
            {},
        ]
        config = cfnlint.config.ConfigMixIn(
            ["--include-checks", "I1234", "I4321", "--merge-configs"]
        )
        config.template_args = {
            "Metadata": {
                "cfn-lint": {
                    "config": {"include_checks": ["I9876"], "ignore_checks": ["W3001"]}
                }
            }
        }
        # config files wins
        self.assertEqual(config.regions, ["us-west-2"])
        # CLI should win
        self.assertEqual(
            config.include_checks, ["W", "E", "I1234", "I4321", "I9876", "I"]
        )
        # template file wins over config file
        self.assertEqual(config.ignore_checks, ["W3001", "E3001"])
