"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from collections import deque

import pytest

from cfnlint.context import Path, create_context_for_template
from cfnlint.helpers import FUNCTIONS
from cfnlint.jsonschema import CfnTemplateValidator
from cfnlint.template import Template


@pytest.fixture
def template(request):
    if hasattr(request, "param"):
        return request.param
    return {}


@pytest.fixture
def regions():
    return ["us-east-1"]


@pytest.fixture
def cfn(template, regions):
    return Template(
        "",
        template,
        regions,
    )


@pytest.fixture
def path(request):
    if hasattr(request, "param"):
        t_path = deque(request.param.get("path", []))
        value_path = deque(request.param.get("value_path", []))
        cfn_path = deque(request.param.get("cfn_path", []))

        return Path(
            path=t_path,
            value_path=value_path,
            cfn_path=cfn_path,
        )

    return Path(
        path=deque(),
        value_path=deque(),
        cfn_path=deque(),
    )


@pytest.fixture
def functions():
    return FUNCTIONS


@pytest.fixture
def strict_types(strict_types=True):
    return strict_types


@pytest.fixture
def context(cfn, path, functions, strict_types):
    return create_context_for_template(cfn).evolve(
        path=path,
        functions=functions,
        strict_types=strict_types,
    )


@pytest.fixture
def validators(request):
    if hasattr(request, "param"):
        return request.param
    return {}


@pytest.fixture
def validator(cfn, context, validators):
    return CfnTemplateValidator({}).extend(validators=validators)(
        context=context,
        cfn=cfn,
        schema={},
    )
