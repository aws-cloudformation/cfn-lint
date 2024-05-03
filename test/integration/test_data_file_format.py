"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import fnmatch
import json
import os
from unittest import TestCase

import pytest

import cfnlint
from cfnlint.helpers import format_json_string


@pytest.mark.data
class TestDataFileFormat(TestCase):
    """Test format of data files"""

    def setUp(self) -> None:
        self.modules = [
            "AdditionalSpecs",
            "CfnLintCli",
            "Serverless",
            "schemas",
        ]
        super().setUp()

    def test_data_module_specs(self):
        """Test data file formats"""

        for module in self.modules:
            append_dir = os.path.join(
                os.path.dirname(cfnlint.__file__),
                "data",
                module,
            )
            for dirpath, _, filenames in os.walk(append_dir):
                for filename in fnmatch.filter(filenames, "*.json"):
                    string_content = ""
                    with open(
                        os.path.join(dirpath, filename), encoding="utf8"
                    ) as input_file:
                        string_content = "".join(input_file.readlines())

                    pretty_content = format_json_string(json.loads(string_content))
                    self.assertEqual(
                        string_content, f"{pretty_content}\n", f"{dirpath}/{filename}"
                    )
