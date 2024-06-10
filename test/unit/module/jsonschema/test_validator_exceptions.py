"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema.exceptions import ValidationError
from cfnlint.jsonschema.validators import CfnTemplateValidator


def fail(validator, errors, instance, schema):
    raise ValueError(f"Bad {errors!r}")


@pytest.fixture
def validator():
    validators = {
        "foo": fail,
        "bar": fail,
    }
    validator = CfnTemplateValidator({}).extend(
        validators=validators,
    )({"foo": True, "bar": False})
    return validator


def test_validator_raises_exception(validator):

    errs = list(validator.iter_errors(""))

    assert errs == [
        ValidationError(
            "Exception 'Bad True' raised while validating 'foo'",
            validator="foo",
            schema_path=deque(["foo"]),
            path=deque([]),
        ),
        ValidationError(
            "Exception 'Bad False' raised while validating 'bar'",
            validator="bar",
            schema_path=deque(["bar"]),
            path=deque([]),
        ),
    ]
