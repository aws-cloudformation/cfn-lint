"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from test.unit.rules import BaseRuleTestCase

from cfnlint.rules.resources.properties.NumberSize import (
    NumberSize,  # pylint: disable=E0401
)


class TestNumberSize(BaseRuleTestCase):
    """Test Number Size Property Configuration"""
