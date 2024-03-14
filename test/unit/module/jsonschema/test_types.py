"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import unittest

from cfnlint.jsonschema._types import TypeChecker, is_null
from cfnlint.jsonschema.exceptions import UndefinedTypeCheck


class TestCfnTypeChecker(unittest.TestCase):
    def test_class(self):
        emptyChecker = TypeChecker()
        self.assertEqual(emptyChecker.type_checkers, {})
        self.assertEqual(str(emptyChecker), "<TypeChecker types={}>")

        with self.assertRaises(UndefinedTypeCheck):
            emptyChecker.is_type("foo", "bar")

    def test_null(self):
        # Only a small number of places can use null
        self.assertTrue(is_null(None, None))
        self.assertFalse(is_null(None, ""))
