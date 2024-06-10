"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.context.context import Path


@pytest.mark.parametrize(
    "name,params,expected",
    [
        (
            "Proper descend",
            {
                "path": "Property",
                "cfn_path": "Property",
                "value_path": "Property",
            },
            Path(
                path=deque(["Property"]),
                cfn_path=deque(["Property"]),
                value_path=deque(["Property"]),
            ),
        ),
        (
            "Exception on using function",
            {
                "path": "Foo",
                "cfn_path": "Fn::If",
            },
            ValueError(),
        ),
        (
            "Exception on using int",
            {
                "path": "Foo",
                "cfn_path": 1,
            },
            ValueError(),
        ),
    ],
)
def test_path_descend(name, params, expected):
    path = Path()
    if isinstance(expected, Exception):
        with pytest.raises(type(expected)):
            path.descend(**params)
    else:
        path = path.descend(**params)
        assert path == expected
