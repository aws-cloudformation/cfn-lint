"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from typing import Any

import pytest

from cfnlint.jsonschema._resolvers_cfn import ResolutionResult, Validator
from cfnlint.jsonschema.validators import CfnTemplateValidator


def _many_resolver(validator: Validator, instance: Any) -> ResolutionResult:
    for i in range(instance):
        yield i, validator, None


@pytest.fixture
def validator():
    validator = CfnTemplateValidator({})
    validator.fn_resolvers = {"Ref": _many_resolver}
    validator.context = validator.context.evolve(functions=["Ref"])
    return validator


class TestResolveMaxYields:
    def test_under_cap(self, validator):
        results = list(validator.resolve_value({"Ref": 100}))
        assert len(results) == 100

    def test_at_cap(self, validator):
        results = list(validator.resolve_value({"Ref": 512}))
        assert len(results) == 512

    def test_over_cap(self, validator):
        results = list(validator.resolve_value({"Ref": 1000}))
        assert len(results) == 512

    def test_no_function_not_capped(self, validator):
        results = list(validator.resolve_value("plain"))
        assert len(results) == 1
        assert results[0][0] == "plain"
