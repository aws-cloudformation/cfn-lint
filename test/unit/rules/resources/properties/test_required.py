"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import json
from test.unit.rules import BaseRuleTestCase

import cfnlint.helpers
from cfnlint.rules.resources.properties.Required import (
    Required,  # pylint: disable=E0401
)


class TestResourceConfiguration(BaseRuleTestCase):
    """Test Resource Properties"""
