"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from pathlib import Path
from test.testlib.testcase import BaseTestCase
from unittest.mock import patch

import cfnlint.core
import cfnlint.helpers  # pylint: disable=E0401


class TestRunCli(BaseTestCase):
    """Test Run Checks"""

    @patch("cfnlint.core.PROVIDER_SCHEMA_MANAGER.patch")
    @patch("cfnlint.core.run_checks")
    def test_run_cli_override_spec(self, run_checks_mock, schema_manager_mock):
        cfnlint.core.run_cli(
            filename="",
            template="",
            rules=[],
            regions=["us-east-1"],
            override_spec="spec",
            build_graph=False,
            registry_schemas=[],
            mandatory_rules=[],
        )
        run_checks_mock.assert_called_with("", "", [], ["us-east-1"], [])
        schema_manager_mock.assert_called_with("spec", ["us-east-1"])

    @patch("cfnlint.core.Template.build_graph")
    @patch("cfnlint.core.run_checks")
    def test_run_cli_build_graph(self, run_checks_mock, build_graph_mock):
        cfnlint.core.run_cli(
            filename="",
            template={"Resources": {"Bucket": {"Type": "AWS::S3::Bucket"}}},
            rules=[],
            regions=["us-east-1"],
            override_spec=None,
            build_graph=True,
            registry_schemas=[],
            mandatory_rules=[],
        )
        run_checks_mock.assert_called_with(
            "",
            {"Resources": {"Bucket": {"Type": "AWS::S3::Bucket"}}},
            [],
            ["us-east-1"],
            [],
        )
        build_graph_mock.assert_called_with()

    @patch("cfnlint.core.PROVIDER_SCHEMA_MANAGER.load_registry_schemas")
    @patch("cfnlint.core.run_checks")
    def test_run_cli_provider_specs(self, run_checks_mock, load_registry_schemas_mock):
        cfnlint.core.run_cli(
            filename="",
            template={},
            rules=[],
            regions=["us-east-1"],
            override_spec=None,
            build_graph=False,
            registry_schemas=[
                "test/fixtures/schemas",
            ],
            mandatory_rules=[],
        )
        run_checks_mock.assert_called_with("", {}, [], ["us-east-1"], [])
        load_registry_schemas_mock.assert_called_with("test/fixtures/schemas")
