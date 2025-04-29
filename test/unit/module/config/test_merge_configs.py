"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import unittest

from cfnlint.config import _merge_configs


class TestMergeConfigs(unittest.TestCase):
    """Test _merge_configs function"""

    def test_merge_lists(self):
        """Test merging lists"""
        cli_value = ["a", "b"]
        template_value = ["c", "d"]
        file_value = ["e", "f"]
        manual_value = ["g", "h"]

        result = _merge_configs(cli_value, template_value, file_value, manual_value)
        self.assertEqual(result, ["a", "b", "c", "d", "e", "f", "g", "h"])

    def test_merge_lists_with_none(self):
        """Test merging lists with None values"""
        cli_value = ["a", "b"]
        template_value = None
        file_value = ["e", "f"]
        manual_value = None

        result = _merge_configs(cli_value, template_value, file_value, manual_value)
        self.assertEqual(result, ["a", "b", "e", "f"])

    def test_merge_lists_with_non_lists(self):
        """Test merging lists with non-list values"""
        cli_value = ["a", "b"]
        template_value = "not a list"
        file_value = {"key": "value"}
        manual_value = 123

        result = _merge_configs(cli_value, template_value, file_value, manual_value)
        self.assertEqual(result, ["a", "b"])

    def test_merge_dicts(self):
        """Test merging dictionaries"""
        cli_value = {"a": 1, "b": 2}
        template_value = {"c": 3, "d": 4}
        file_value = {"e": 5, "f": 6}
        manual_value = {"g": 7, "h": 8}

        result = _merge_configs(cli_value, template_value, file_value, manual_value)
        self.assertEqual(
            result, {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5, "f": 6, "g": 7, "h": 8}
        )

    def test_merge_dicts_with_none(self):
        """Test merging dictionaries with None values"""
        cli_value = {"a": 1, "b": 2}
        template_value = None
        file_value = {"e": 5, "f": 6}
        manual_value = None

        result = _merge_configs(cli_value, template_value, file_value, manual_value)
        self.assertEqual(result, {"a": 1, "b": 2, "e": 5, "f": 6})

    def test_merge_dicts_with_non_dicts(self):
        """Test merging dictionaries with non-dict values"""
        cli_value = {"a": 1, "b": 2}
        template_value = "not a dict"
        file_value = ["e", "f"]
        manual_value = 123

        result = _merge_configs(cli_value, template_value, file_value, manual_value)
        self.assertEqual(result, {"a": 1, "b": 2})

    def test_merge_dicts_with_overlapping_keys(self):
        """Test merging dictionaries with overlapping keys"""
        cli_value = {"a": 1, "b": 2, "common": "cli"}
        template_value = {"c": 3, "d": 4, "common": "template"}
        file_value = {"e": 5, "f": 6, "common": "file"}
        manual_value = {"g": 7, "h": 8, "common": "manual"}

        result = _merge_configs(cli_value, template_value, file_value, manual_value)
        # Last one in wins for overlapping keys
        self.assertEqual(
            result,
            {
                "a": 1,
                "b": 2,
                "c": 3,
                "d": 4,
                "e": 5,
                "f": 6,
                "g": 7,
                "h": 8,
                "common": "manual",
            },
        )

    def test_merge_non_list_non_dict(self):
        """Test merging when cli_value is neither list nor dict"""
        cli_value = "string"
        template_value = ["c", "d"]
        file_value = {"e": 5}
        manual_value = 123

        result = _merge_configs(cli_value, template_value, file_value, manual_value)
        self.assertIsNone(result)

    def test_merge_empty_values(self):
        """Test merging with empty values"""
        cli_value = []
        template_value = []
        file_value = []
        manual_value = []

        result = _merge_configs(cli_value, template_value, file_value, manual_value)
        self.assertEqual(result, [])

        cli_value = {}
        template_value = {}
        file_value = {}
        manual_value = {}

        result = _merge_configs(cli_value, template_value, file_value, manual_value)
        self.assertEqual(result, {})
