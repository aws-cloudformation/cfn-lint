"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.integration import BaseCliTestCase

from cfnlint import ConfigMixIn


class TestQuickStartTemplates(BaseCliTestCase):
    """Test QuickStart Templates Parsing"""

    scenarios = [
        {
            "filename": (
                "test/fixtures/templates/integration"
                "/resources-cloudformation-init.yaml"
            ),
            "results_filename": (
                "test/fixtures/results/integration/"
                "resources-cloudformation-init.json"
            ),
            "exit_code": 0,
        },
        {
            "filename": "test/fixtures/templates/integration/dynamic-references.yaml",
            "results_filename": (
                "test/fixtures/results/integration/dynamic-references.json"
            ),
            "exit_code": 2,
        },
        {
            "filename": "test/fixtures/templates/integration/ref-no-value.yaml",
            "results_filename": ("test/fixtures/results/integration/ref-no-value.json"),
            "exit_code": 2,
        },
        {
            "filename": "test/fixtures/templates/integration/metdata.yaml",
            "results_filename": ("test/fixtures/results/integration/metadata.json"),
            "exit_code": 4,
        },
        {
            "filename": ("test/fixtures/templates/integration/availability-zones.yaml"),
            "results_filename": (
                "test/fixtures/results/integration/availability-zones.json"
            ),
            "exit_code": 2,
        },
        {
            "filename": ("test/fixtures/templates/integration/getatt-types.yaml"),
            "results_filename": ("test/fixtures/results/integration/getatt-types.json"),
            "exit_code": 10,
        },
        {
            "filename": ("test/fixtures/templates/integration/ref-types.yaml"),
            "results_filename": ("test/fixtures/results/integration/ref-types.json"),
            "exit_code": 2,
        },
        {
            "filename": ("test/fixtures/templates/integration/formats.yaml"),
            "results_filename": ("test/fixtures/results/integration/formats.json"),
            "exit_code": 2,
        },
        {
            "filename": (
                "test/fixtures/templates/integration/aws-ec2-networkinterface.yaml"
            ),
            "results_filename": (
                "test/fixtures/results/integration/aws-ec2-networkinterface.json"
            ),
            "exit_code": 2,
        },
        {
            "filename": ("test/fixtures/templates/integration/aws-ec2-instance.yaml"),
            "results_filename": (
                "test/fixtures/results/integration/aws-ec2-instance.json"
            ),
            "exit_code": 2,
        },
        {
            "filename": (
                "test/fixtures/templates/integration/aws-ec2-launchtemplate.yaml"
            ),
            "results_filename": (
                "test/fixtures/results/integration/aws-ec2-launchtemplate.json"
            ),
            "exit_code": 2,
        },
        {
            "filename": ("test/fixtures/templates/integration/aws-ec2-subnet.yaml"),
            "results_filename": (
                "test/fixtures/results/integration/aws-ec2-subnet.json"
            ),
            "exit_code": 2,
        },
        {
            "filename": ("test/fixtures/templates/integration/aws-dynamodb-table.yaml"),
            "results_filename": (
                "test/fixtures/results/integration/aws-dynamodb-table.json"
            ),
            "exit_code": 2,
        },
    ]

    def test_templates(self):
        """Test same templates using integration approach"""
        self.run_module_integration_scenarios(
            ConfigMixIn(
                [],
                include_checks=["I"],
                include_experimental=True,
            )
        )
