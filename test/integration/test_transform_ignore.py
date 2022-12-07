"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.integration import BaseCliTestCase

import cfnlint.core


class TestTransformIgnore(BaseCliTestCase):
    """Test Ignoring Transform Failure"""

    scenarios = [
        {
            "filename": "test/fixtures/templates/bad/transform_serverless_template.yaml",
            "exit_code": 0,
        },
    ]

    def test_templates(self):
        """Test same templates using integration approach"""
        rules = cfnlint.core.get_rules([], ["E0001"], ["I", "E", "W"], {}, True)
        self.run_module_integration_scenarios(rules)
