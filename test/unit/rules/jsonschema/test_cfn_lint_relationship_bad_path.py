"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from collections import deque

import pytest

from cfnlint.context import Path
from cfnlint.rules.jsonschema.CfnLintRelationship import CfnLintRelationship


@pytest.fixture
def rule():
    return CfnLintRelationship(keywords=[], relationship="Resources")


@pytest.fixture
def template():
    return {
        "AWSTemplateFormatVersion": "2010-09-09",
        "Resources": {},
    }


def test_get_relationships(rule, validator):
    validator = validator.evolve(
        context=validator.context.evolve(
            path=Path(
                deque(["Resources", "ParentOne", "Properties", "ImageId"]),
            ),
        ),
    )
    assert [] == list(rule.get_relationship(validator))
