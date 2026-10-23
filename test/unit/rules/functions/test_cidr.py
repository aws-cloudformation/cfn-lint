"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.helpers import load_resource
from cfnlint.jsonschema import ValidationError
from cfnlint.rules.functions.Cidr import Cidr


@pytest.fixture(scope="module")
def rule():
    rule = Cidr()
    yield rule


@pytest.mark.parametrize(
    "name,instance,schema,expected",
    [
        (
            "Valid Fn::Cidr with 2 element array",
            {"Fn::Cidr": ["192.168.0.0/24", 6]},
            {"type": "array"},
            [],
        ),
        (
            "Valid Fn::Cidr with 3 element array",
            {"Fn::Cidr": ["192.168.0.0/24", 6, 5]},
            {"type": "array"},
            [],
        ),
        (
            "Invalid Fn::Cidr with wrong output type",
            {"Fn::Cidr": ["192.168.0.0/24", 2]},
            {"type": "string"},
            [
                ValidationError(
                    "{'Fn::Cidr': ['192.168.0.0/24', 2]} is not of type 'string'",
                    path=deque([]),
                    schema_path=deque([]),
                    validator="fn_cidr",
                ),
            ],
        ),
        (
            "Invalid Fn::Cidr is NOT a array",
            {"Fn::Cidr": "foo"},
            {"type": "array"},
            [
                ValidationError(
                    "'foo' is not of type 'array'",
                    path=deque(["Fn::Cidr"]),
                    schema_path=deque(["cfnContext", "schema", "type"]),
                    validator="fn_cidr",
                ),
            ],
        ),
        (
            "Valid Fn::Cidr with a valid function",
            {"Fn::Cidr": ["192.168.0.0/24", {"Fn::FindInMap": ["A", "B", "D"]}]},
            {"type": "array"},
            [],
        ),
        (
            "Valid Fn::Cidr with an IPv6 ipBlock",
            {"Fn::Cidr": ["2001:db8:1234:1a00::/56", 2, 64]},
            {"type": "array"},
            [],
        ),
        (
            "Valid Fn::Cidr with a compressed IPv6 ipBlock",
            {"Fn::Cidr": ["::1/128", 2, 128]},
            {"type": "array"},
            [],
        ),
        (
            "Valid Fn::Cidr with a full IPv6 ipBlock",
            {"Fn::Cidr": ["2001:0db8:0000:0000:0000:0000:0000:0001/64", 2, 64]},
            {"type": "array"},
            [],
        ),
        (
            "Invalid Fn::Cidr with an invalid function",
            {"Fn::Cidr": ["192.168.0.0/24", {"Fn::Join": ["-", "bar"]}]},
            {"type": "array"},
            [
                ValidationError(
                    "{'Fn::Join': ['-', 'bar']} is not of type 'integer'",
                    path=deque(["Fn::Cidr", 1]),
                    schema_path=deque(
                        [
                            "cfnContext",
                            "schema",
                            "prefixItems",
                            1,
                            "cfnContext",
                            "schema",
                            "type",
                        ]
                    ),
                    validator="fn_cidr",
                ),
            ],
        ),
    ],
)
def test_validate(name, instance, schema, expected, rule, validator):
    errs = list(rule.fn_cidr(validator, schema, instance, {}))
    assert errs == expected, f"Test {name!r} got {errs!r}"


@pytest.mark.parametrize(
    "ip_block,is_valid",
    [
        # IPv6 blocks CloudFormation accepts (issue #4855)
        ("2001:db8:1234:1a00::/56", True),
        ("::1/128", True),
        ("::/0", True),
        ("fe80::/10", True),
        ("2001:0DB8::1/64", True),
        ("1:2:3:4:5:6:7:8/128", True),
        ("2001:db8::/32", True),
        # IPv4 behavior is unchanged
        ("192.168.0.0/24", True),
        ("10.0.0.0/16", True),
        ("0.0.0.0/0", True),
        # malformed blocks stay rejected
        ("2001:db8::1/129", False),
        ("2001:db8:::1/64", False),
        ("12345::/64", False),
        ("gggg::1/64", False),
        ("1:2:3:4:5:6:7:8:9/64", False),
        ("2001:db8::1/", False),
        ("10.0.0.0/33", False),
        ("256.1.1.1/24", False),
    ],
)
def test_cidr_ip_block_pattern(ip_block, is_valid):
    """The ipBlock pattern accepts IPv6 CIDR notation without weakening IPv4."""
    import re

    schema = load_resource("cfnlint.data.schemas.other.functions", "cidr.json")
    pattern = schema["cfnContext"]["schema"]["prefixItems"][0]["cfnContext"][
        "schema"
    ]["pattern"]
    assert bool(re.match(pattern, ip_block)) is is_valid, ip_block


@pytest.mark.parametrize(
    "ip_block",
    [
        "2001:db8::1/129",
        "2001:db8:::1/64",
    ],
)
def test_invalid_ipv6_cidr_reports_error(ip_block, rule, validator):
    """Malformed IPv6 blocks surface as E1024 through the rule path."""
    errs = list(
        rule.fn_cidr(
            validator, {"type": "array"}, {"Fn::Cidr": [ip_block, 2, 64]}, {}
        )
    )
    assert len(errs) == 1
    assert errs[0].validator == "fn_cidr"
    assert list(errs[0].path) == ["Fn::Cidr", 0]
    assert errs[0].message.startswith(f"{ip_block!r} does not match")
