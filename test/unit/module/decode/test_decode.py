"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import json
import logging
from test.testlib.testcase import BaseTestCase
from unittest.mock import patch

import yaml
from yaml.scanner import ScannerError

import cfnlint.decode.cfn_json
import cfnlint.decode.cfn_yaml
import cfnlint.decode.decode


class TestDecode(BaseTestCase):
    def tearDown(self) -> None:
        super().tearDown()
        logger = logging.getLogger("cfnlint.decode.decode")
        logger.disabled = False

    def setUp(self):
        """Setup"""
        logger = logging.getLogger("cfnlint.decode.decode")
        logger.disabled = True

    @patch("cfnlint.decode.cfn_yaml.load")
    def test_decode_permission_error(self, mock_cfn_yaml):
        mock_cfn_yaml.side_effect = OSError(13, "Permission denied")
        _, matches = cfnlint.decode.decode(filename="test")
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].rule.id, "E0000")

    @patch("cfnlint.decode.cfn_yaml.load")
    def test_decode_unicode_error(self, mock_cfn_yaml):
        mock_cfn_yaml.side_effect = UnicodeDecodeError("", b"\x00\x00", 0, 0, "reason")
        _, matches = cfnlint.decode.decode(filename="test")
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].rule.id, "E0000")

    @patch("cfnlint.decode.cfn_yaml.load")
    def test_decode_scanner_error_other(self, mock_cfn_yaml):
        mock_cfn_yaml.side_effect = ScannerError(
            problem="foo", problem_mark=yaml.Mark("test", 0, 0, 0, "", 0)
        )
        _, matches = cfnlint.decode.decode(filename="test")
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].rule.id, "E0000")
        self.assertEqual(matches[0].message, "foo")

    @patch("cfnlint.decode.cfn_yaml.load")
    @patch("cfnlint.decode.cfn_json.load")
    def test_decode_scanner_error_tab(self, mock_cfn_json, mock_cfn_yaml):
        mock_cfn_json.return_value = {}
        mock_cfn_yaml.side_effect = ScannerError(
            problem="found character '\\t' that cannot start any token"
        )
        _, matches = cfnlint.decode.decode("test")
        self.assertListEqual(matches, [])
        mock_cfn_json.assert_called_once()

    @patch("cfnlint.decode.cfn_yaml.load")
    @patch("cfnlint.decode.cfn_json.load")
    def test_decode_json_decoder_no_json_error(self, mock_cfn_json, mock_cfn_yaml):
        mock_cfn_json.side_effect = json.JSONDecodeError(
            "No JSON object could be decoded", "", 0
        )
        mock_cfn_yaml.side_effect = ScannerError(
            problem="found character '\\t' that cannot start any token",
            problem_mark=yaml.Mark("test", 0, 0, 0, "", 0),
        )
        _, matches = cfnlint.decode.decode("test")
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].rule.id, "E0000")

    @patch("cfnlint.decode.cfn_yaml.load")
    @patch("cfnlint.decode.cfn_json.load")
    def test_decode_json_decoder_exception_error(self, mock_cfn_json, mock_cfn_yaml):
        mock_cfn_json.side_effect = Exception("foo")
        mock_cfn_yaml.side_effect = ScannerError(
            problem="found character '\\t' that cannot start any token",
            problem_mark=yaml.Mark("test", 0, 0, 0, "", 0),
        )
        _, matches = cfnlint.decode.decode("test")
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].rule.id, "E0000")
        self.assertEqual(
            matches[0].message, "Tried to parse test as JSON but got error: foo"
        )

    @patch("cfnlint.decode.cfn_yaml.load")
    @patch("cfnlint.decode.cfn_json.load")
    def test_decode_json_decoder_expecting_value_error(
        self, mock_cfn_json, mock_cfn_yaml
    ):
        mock_cfn_json.side_effect = json.JSONDecodeError("Expecting value", "", 0)
        mock_cfn_yaml.side_effect = ScannerError(
            problem="found character '\\t' that cannot start any token",
            problem_mark=yaml.Mark("test", 0, 99, 0, "", 0),
        )
        _, matches = cfnlint.decode.decode("test")
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].rule.id, "E0000")
        self.assertEqual(matches[0].linenumber, 100)

    @patch("cfnlint.decode.cfn_yaml.load")
    @patch("cfnlint.decode.cfn_json.load")
    def test_decode_json_decoder_error(self, mock_cfn_json, mock_cfn_yaml):
        err_msg = "Foo"
        mock_cfn_json.side_effect = json.JSONDecodeError(err_msg, "", 0)
        mock_cfn_yaml.side_effect = ScannerError(
            problem="found character '\\t' that cannot start any token"
        )
        _, matches = cfnlint.decode.decode("test")
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].rule.id, "E0000")
        self.assertEqual(matches[0].message, "Foo")

    @patch("cfnlint.decode.cfn_yaml.load")
    def test_decode_yaml_error(self, mock_cfn_yaml):
        err_msg = "Foo"
        mock_cfn_yaml.side_effect = yaml.YAMLError(err_msg)
        _, matches = cfnlint.decode.decode("test")
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].rule.id, "E0000")
        self.assertEqual(matches[0].message, err_msg)

    def test_decode_yaml_null_key(self):
        err_msg = "Null key 'null' not supported (line 3)"
        with self.assertRaises(cfnlint.decode.cfn_yaml.CfnParseError) as e:
            cfnlint.decode.cfn_yaml.loads(
                """
                Parameters:
                    null: test
            """
            )
        self.assertEqual(str(e.exception), err_msg)

    def test_decode_yaml_empty(self):
        template = cfnlint.decode.cfn_yaml.loads("")
        self.assertEqual(template, {})
