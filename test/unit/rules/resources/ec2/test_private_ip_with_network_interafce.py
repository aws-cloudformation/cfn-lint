"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.ectwo.PrivateIpWithNetworkInterface import (
    PrivateIpWithNetworkInterface,
)


@pytest.fixture(scope="module")
def rule():
    rule = PrivateIpWithNetworkInterface()
    yield rule


@pytest.mark.parametrize(
    "name,instance,path,expected",
    [
        (
            "Valid with no Private Ip Address",
            {
                "NetworkInterfaces": [
                    {
                        "PrivateIpAddresses": [
                            {"PrivateIpAddress": "172.31.35.42", "Primary": True}
                        ]
                    }
                ]
            },
            {
                "path": ["Resources", "Instance", "Properties"],
            },
            [],
        ),
        (
            "Valid with Private Ip Address with Primary False",
            {
                "PrivateIpAddress": "172.31.35.42",
                "NetworkInterfaces": [
                    {
                        "PrivateIpAddresses": [
                            {"PrivateIpAddress": "172.31.35.42", "Primary": False}
                        ]
                    }
                ],
            },
            {
                "path": ["Resources", "Instance", "Properties"],
            },
            [],
        ),
        (
            "Valid with Private Ip Address without Primary specified",
            {
                "PrivateIpAddress": "172.31.35.42",
                "NetworkInterfaces": [
                    {"PrivateIpAddresses": [{"PrivateIpAddress": "172.31.35.42"}]}
                ],
            },
            {
                "path": ["Resources", "Instance", "Properties"],
            },
            [],
        ),
        (
            "Valid AWS::EC2::NetworkInterface with PrivateIpAddresses",
            {
                "PrivateIpAddress": "172.31.35.42",
                "PrivateIpAddresses": [
                    {"PrivateIpAddress": "172.31.35.42", "Primary": False}
                ],
            },
            {
                "path": ["Resources", "Instance", "Properties"],
            },
            [],
        ),
        (
            "Invalid with a private ip address in two spots",
            {
                "PrivateIpAddress": "172.31.35.42",
                "NetworkInterfaces": [
                    {
                        "PrivateIpAddress": "172.31.35.42",
                    }
                ],
            },
            {
                "path": ["Resources", "Instance", "Properties"],
            },
            [
                ValidationError(
                    "'Primary' cannot be True when 'PrivateIpAddress' is specified",
                    validator=None,
                    rule=PrivateIpWithNetworkInterface(),
                    path=deque(["NetworkInterfaces", 0, "PrivateIpAddress"]),
                    schema_path=deque(
                        [
                            "then",
                            "properties",
                            "NetworkInterfaces",
                            "items",
                            "properties",
                            "PrivateIpAddress",
                        ]
                    ),
                )
            ],
        ),
        (
            "Invalid with a private ip address",
            {
                "PrivateIpAddress": "172.31.35.42",
                "NetworkInterfaces": [
                    {
                        "PrivateIpAddresses": [
                            {"PrivateIpAddress": "172.31.35.42", "Primary": True}
                        ]
                    }
                ],
            },
            {
                "path": ["Resources", "Instance", "Properties"],
            },
            [
                ValidationError(
                    "'Primary' cannot be True when 'PrivateIpAddress' is specified",
                    validator="enum",
                    rule=PrivateIpWithNetworkInterface(),
                    path=deque(
                        ["NetworkInterfaces", 0, "PrivateIpAddresses", 0, "Primary"]
                    ),
                    schema_path=deque(
                        [
                            "then",
                            "properties",
                            "NetworkInterfaces",
                            "items",
                            "properties",
                            "PrivateIpAddresses",
                            "items",
                            "properties",
                            "Primary",
                            "enum",
                        ]
                    ),
                )
            ],
        ),
        (
            "Invalid AWS::EC2::NetworkInterface with PrivateIpAddresses",
            {
                "PrivateIpAddress": "172.31.35.42",
                "PrivateIpAddresses": [
                    {"PrivateIpAddress": "172.31.35.42", "Primary": True}
                ],
            },
            {
                "path": ["Resources", "Instance", "Properties"],
            },
            [
                ValidationError(
                    "'Primary' cannot be True when 'PrivateIpAddress' is specified",
                    validator="enum",
                    rule=PrivateIpWithNetworkInterface(),
                    path=deque(["PrivateIpAddresses", 0, "Primary"]),
                    schema_path=deque(
                        [
                            "then",
                            "properties",
                            "PrivateIpAddresses",
                            "items",
                            "properties",
                            "Primary",
                            "enum",
                        ]
                    ),
                )
            ],
        ),
    ],
    indirect=["path"],
)
def test_validate(name, instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))

    assert (
        errs == expected
    ), f"Expected test {name!r} to have {expected!r} but got {errs!r}"
