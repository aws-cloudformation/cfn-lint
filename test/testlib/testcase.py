"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from unittest import TestCase

import cfnlint.decode.cfn_yaml


class BaseTestCase(TestCase):
    """
    All test cases should inherit from this class as any common
    functionality that is added here will then be available to all
    subclasses. This facilitates the ability to update in one spot
    and allow all tests to get the update for easy maintenance.
    """

    def load_template(self, filename):
        """Return template"""
        return cfnlint.decode.cfn_yaml.load(filename)

    def assertEqualListOfDicts(self, a, b):
        """Compare two lists of dicts"""
        assert isinstance(a, list)
        assert isinstance(b, list)

        def key_func(d):
            """sort dict based on keys"""
            items = ((k, v if v is not None else "") for k, v in d.items())
            return sorted(items)

        self.assertEqual(sorted(a, key=key_func), sorted(b, key=key_func))
