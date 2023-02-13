"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.resources.properties.ListSize import (
    ListSize,  # pylint: disable=E0401
)


class TestListSize(BaseRuleTestCase):
    """Test List Size Property Configuration"""
