"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import unittest

from cfnlint.jsonschema._format import cfn_format_checker
from cfnlint.jsonschema.exceptions import FormatError


class TestFormat(unittest.TestCase):
    def test_format_checker(self):
        self.assertEqual(
            str(cfn_format_checker),
            (
                "<FormatChecker checkers=['date', 'date-time',"
                " 'email', 'ipv4', 'ipv6', 'regex', 'time']>"
            ),
        )

        self.assertIsNone(cfn_format_checker.check("aws@amazon.com", "email"))
        self.assertIsNone(cfn_format_checker.check({"foo": "bar"}, "email"))
        with self.assertRaises(FormatError):
            cfn_format_checker.check("foo", "email")

        self.assertIsNone(cfn_format_checker.check("127.0.0.1", "ipv4"))
        self.assertIsNone(cfn_format_checker.check({"foo": "bar"}, "ipv4"))
        with self.assertRaises(FormatError):
            cfn_format_checker.check("foo", "ipv4")

        self.assertIsNone(
            cfn_format_checker.check("0000:0000:0000:0000:0000:0000:0000:0000", "ipv6")
        )
        self.assertIsNone(cfn_format_checker.check({"foo": "bar"}, "ipv6"))
        with self.assertRaises(FormatError):
            cfn_format_checker.check("foo", "ipv6")

        self.assertIsNone(cfn_format_checker.check("1970-01-01", "date"))
        self.assertIsNone(cfn_format_checker.check({"foo": "bar"}, "date"))
        with self.assertRaises(FormatError):
            cfn_format_checker.check("foo", "date")

        self.assertIsNone(
            cfn_format_checker.check("1970-01-01T00:00:00.000Z", "date-time")
        )
        self.assertIsNone(cfn_format_checker.check({"foo": "bar"}, "date-time"))
        with self.assertRaises(FormatError):
            cfn_format_checker.check("foo", "date-time")

        self.assertIsNone(cfn_format_checker.check("00:00:00.000Z", "time"))
        self.assertIsNone(cfn_format_checker.check({"foo": "bar"}, "time"))
        with self.assertRaises(FormatError):
            cfn_format_checker.check("foo", "time")

        self.assertIsNone(cfn_format_checker.check("^$", "regex"))
        self.assertIsNone(cfn_format_checker.check({"foo": "bar"}, "regex"))
        with self.assertRaises(FormatError):
            cfn_format_checker.check("[a-", "regex")
