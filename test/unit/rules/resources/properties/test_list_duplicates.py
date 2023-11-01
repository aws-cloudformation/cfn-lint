"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import pytest

from cfnlint.jsonschema import CfnTemplateValidator
from cfnlint.rules.resources.properties.ListDuplicates import ListDuplicates
from cfnlint.rules.resources.properties.ListDuplicatesAllowed import (
    ListDuplicatesAllowed,
)


@pytest.fixture(scope="module")
def rule():
    rule = ListDuplicates()
    rule.child_rules["I3037"] = ListDuplicatesAllowed()
    yield rule


@pytest.fixture(scope="module")
def validator():
    yield CfnTemplateValidator(schema={})


@pytest.mark.parametrize(
    "instance,uI,schema,expected",
    [
        (["foo", "bar"], True, {}, None),
        (["foo", "bar"], False, {}, None),
        (["foo", "foo"], False, {}, "I3037"),
        (["foo", "foo"], True, {}, "E3037"),
    ],
)
def test_unique_items_fails(instance, uI, expected, rule, schema, validator):
    errs = list(rule.uniqueItems(validator, uI, instance, schema))
    if expected is None:
        assert not errs
    else:
        assert len(errs) == 1
        if expected != "E3037":
            assert errs[0].rule.id == expected
