"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.context import Context
from cfnlint.context.context import Parameter, Resource
from cfnlint.jsonschema import CfnTemplateValidator
from cfnlint.rules.functions._BaseFn import BaseFn


@pytest.fixture(scope="module")
def rule():
    rule = BaseFn()
    yield rule


@pytest.fixture(scope="module")
def validator():
    context = Context(
        regions=["us-east-1"],
        resources={"MyResource": Resource({"Type": "Foo", "Properties": {"A": "B"}})},
        parameters={"MyParameter": Parameter({"Type": "String"})},
    )
    yield CfnTemplateValidator(context=context)
