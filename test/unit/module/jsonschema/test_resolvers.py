"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import unittest
from collections import namedtuple
from typing import List, Tuple

import pytest

from cfnlint.context import Context
from cfnlint.context.context import Resource, Transforms
from cfnlint.helpers import FUNCTIONS, REGIONS
from cfnlint.jsonschema.exceptions import UnknownType
from cfnlint.jsonschema.validators import CfnTemplateValidator


def _resolve(name, instance, expected_results, **kwargs):
    validator = CfnTemplateValidator().evolve(**kwargs)

    resolutions = list(validator.resolve(instance))

    assert resolutions == expected_results


@pytest.mark.parametrize(
    "name,instance,response",
    [
        (
            "Valid Ref with a single instance",
            {"Ref": {"Ref": "MyResource"}},
            [],
        ),
    ],
)
def test_resolvers_ref(name, instance, response):
    _resolve(name, instance, response)
