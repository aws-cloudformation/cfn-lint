"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import unittest
from collections import deque

from cfnlint.jsonschema.exceptions import (
    FormatError,
    UndefinedTypeCheck,
    ValidationError,
    best_match,
)
from cfnlint.rules import CloudFormationLintRule


class _RuleX(CloudFormationLintRule):
    id = "X0000"


class _RuleY(CloudFormationLintRule):
    id = "Y0000"


class TestExceptions(unittest.TestCase):
    def test_validation_error(self):
        err = ValidationError(
            message="Failure", path=deque(["foo"]), schema_path=deque(["bar"])
        )

        self.assertListEqual(list(err.absolute_path), ["foo"])

        self.assertListEqual(list(err.absolute_schema_path), ["bar"])

        self.assertEqual(err.json_path, "$.foo")

    def test_validation_parent_error(self):
        parent = ValidationError(
            message="Failure", path=deque(["foo"]), schema_path=deque(["foo"])
        )
        err = ValidationError(
            message="Failure",
            path=deque(["bar", 0]),
            schema_path=deque(["bar"]),
            parent=parent,
        )

        self.assertListEqual(list(err.absolute_path), ["foo", "bar", 0])

        self.assertListEqual(list(err.absolute_schema_path), ["foo", "bar"])

        self.assertEqual(err.json_path, "$.foo.bar[0]")

    def test_best_match(self):
        one = ValidationError(message="One", path=deque(["foo", "bar", "foo"]))
        two = ValidationError(message="Two", path=deque(["foo", "bar"]))

        self.assertEqual(best_match([one, two]).message, "Two")

        three = ValidationError(
            message="Three",
            path=deque(["foo"]),
            context=[
                ValidationError(message="Four", path=deque(["a", "b"])),
                ValidationError(message="Five", path=deque(["a", "b", "c", "d"])),
                ValidationError(message="Size", path=deque(["a"])),
            ],
        )
        self.assertEqual(best_match([one, two, three]).message, "Five")

        self.assertEqual(best_match([]), None)

    def test_undefined_type_check(self):
        err = UndefinedTypeCheck("foo")
        self.assertEqual(str(err), "Type 'foo' is unknown to this type checker")

    def test_format_error(self):
        err = FormatError("foo")
        self.assertEqual(str(err), "foo")

    def test_equals(self):
        self.assertEqual(
            ValidationError(message="Failure", path=deque(["foo"])),
            ValidationError(message="Failure", path=deque(["foo"])),
        )

        self.assertNotEqual(
            ValidationError(message="Failure", path=deque(["foo"])),
            ValidationError(message="Failure", path=deque(["foo"]), rule=_RuleX()),
        )
        self.assertNotEqual(
            ValidationError(message="Failure", path=deque(["foo"]), rule=_RuleX()),
            ValidationError(
                message="Failure",
                path=deque(["foo"]),
            ),
        )
        self.assertNotEqual(
            ValidationError(message="Failure", path=deque(["foo"]), rule=_RuleX()),
            ValidationError(
                message="Failure",
                path=deque(["foo"]),
                rule=_RuleY(),
            ),
        )
        self.assertNotEqual(
            ValidationError(message="Failure", path=deque(["foo"]), rule=_RuleX()),
            "test",
        )
