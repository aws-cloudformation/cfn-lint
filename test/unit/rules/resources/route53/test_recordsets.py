"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from collections import deque

import pytest

from cfnlint.jsonschema import ValidationError
from cfnlint.rules.resources.route53.RecordSet import RecordSet


@pytest.fixture(scope="module")
def rule():
    rule = RecordSet()
    yield rule


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            {
                "Type": "A",
                "ResourceRecords": ["127.0.0.1"],
            },
            [],
        ),
        (
            {
                "Type": "A",
                "ResourceRecords": ["domain.local"],
            },
            [
                ValidationError(
                    "'domain.local' is not a 'ipv4'",
                    rule=RecordSet(),
                    path=deque(["ResourceRecords", 0]),
                    validator="format",
                    schema_path=deque(
                        [
                            "allOf",
                            0,
                            "then",
                            "properties",
                            "ResourceRecords",
                            "items",
                            "format",
                        ]
                    ),
                )
            ],
        ),
        (
            {
                "Type": "TXT",
                "ResourceRecords": [
                    '"MS=ms123123"',
                    # 255 "a" characters + quotes
                    '"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"',
                    # 255 "a" characters and 255 "b" characters
                    '"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa""bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"',
                    # 255 "a" characters and 255 "b" characters and
                    # 255 "c" characters with a space between b and c
                    '"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa""bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb" "ccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc"',  # noqa: E501
                ],
            },
            [],
        ),
        (
            {
                "Type": "TXT",
                "ResourceRecords": [
                    # 256 "a" characters - too long
                    '"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"',
                    # 256 "b" characters in a second record - too long
                    '"a""bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"',
                    '"MS=ms123123"',
                    # No quotation
                    "test2",
                ],
            },
            [
                ValidationError(
                    '\'"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"\' does not match \'^("[^"]{1,255}" *)*"[^"]{1,255}"$\'',  # noqa: E501
                    rule=RecordSet(),
                    path=deque(["ResourceRecords", 0]),
                    validator="pattern",
                    schema_path=deque(
                        [
                            "allOf",
                            12,
                            "then",
                            "properties",
                            "ResourceRecords",
                            "items",
                            "pattern",
                        ]
                    ),
                ),
                ValidationError(
                    '\'"a""bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"\' does not match \'^("[^"]{1,255}" *)*"[^"]{1,255}"$\'',  # noqa: E501
                    rule=RecordSet(),
                    path=deque(["ResourceRecords", 1]),
                    validator="pattern",
                    schema_path=deque(
                        [
                            "allOf",
                            12,
                            "then",
                            "properties",
                            "ResourceRecords",
                            "items",
                            "pattern",
                        ]
                    ),
                ),
                ValidationError(
                    '\'test2\' does not match \'^("[^"]{1,255}" *)*"[^"]{1,255}"$\'',
                    rule=RecordSet(),
                    path=deque(["ResourceRecords", 3]),
                    validator="pattern",
                    schema_path=deque(
                        [
                            "allOf",
                            12,
                            "then",
                            "properties",
                            "ResourceRecords",
                            "items",
                            "pattern",
                        ]
                    ),
                ),
            ],
        ),
        (
            {
                "Type": "AAAA",
                "ResourceRecords": [
                    "2001:0db8:85a3:0:0:8a2e:0370:7334",
                    "2001:0db8:3c4d:0015:0000:0000:1a2f:1a2b",
                    "0:0:0:0:0:0:A00:1",
                ],
            },
            [],
        ),
        (
            {
                "Type": "AAAA",
                "ResourceRecords": [
                    # IPv4 address
                    "127.0.0.1",
                    # Invalid data
                    "XXXX:XXXX:XXXX:XXXX:XXXX:XXXX:1.2.3.4",
                    # Spaces
                    "2001:0db8: 85a3:0:0:8a2e:0370:7334",
                    # Missing components
                    "1111:2222:3333:4444:5555:6666:7777",
                    # Too much components
                    "1111:2222:3333:4444:5555:6666:7777:8888::",
                ],
            },
            [
                ValidationError(
                    "'127.0.0.1' is not a 'ipv6'",
                    rule=RecordSet(),
                    path=deque(["ResourceRecords", 0]),
                    validator="format",
                    schema_path=deque(
                        [
                            "allOf",
                            1,
                            "then",
                            "properties",
                            "ResourceRecords",
                            "items",
                            "format",
                        ]
                    ),
                ),
                ValidationError(
                    "'XXXX:XXXX:XXXX:XXXX:XXXX:XXXX:1.2.3.4' is not a 'ipv6'",
                    rule=RecordSet(),
                    path=deque(["ResourceRecords", 1]),
                    validator="format",
                    schema_path=deque(
                        [
                            "allOf",
                            1,
                            "then",
                            "properties",
                            "ResourceRecords",
                            "items",
                            "format",
                        ]
                    ),
                ),
                ValidationError(
                    "'2001:0db8: 85a3:0:0:8a2e:0370:7334' is not a 'ipv6'",
                    rule=RecordSet(),
                    path=deque(["ResourceRecords", 2]),
                    validator="format",
                    schema_path=deque(
                        [
                            "allOf",
                            1,
                            "then",
                            "properties",
                            "ResourceRecords",
                            "items",
                            "format",
                        ]
                    ),
                ),
                ValidationError(
                    "'1111:2222:3333:4444:5555:6666:7777' is not a 'ipv6'",
                    rule=RecordSet(),
                    path=deque(["ResourceRecords", 3]),
                    validator="format",
                    schema_path=deque(
                        [
                            "allOf",
                            1,
                            "then",
                            "properties",
                            "ResourceRecords",
                            "items",
                            "format",
                        ]
                    ),
                ),
                ValidationError(
                    "'1111:2222:3333:4444:5555:6666:7777:8888::' is not a 'ipv6'",
                    rule=RecordSet(),
                    path=deque(["ResourceRecords", 4]),
                    validator="format",
                    schema_path=deque(
                        [
                            "allOf",
                            1,
                            "then",
                            "properties",
                            "ResourceRecords",
                            "items",
                            "format",
                        ]
                    ),
                ),
            ],
        ),
        (
            {
                "Type": "CAA",
                "ResourceRecords": [
                    '0 issue "amazontrust.com;"',
                    '0 issue "awstrust.com;"',
                    '0 issue "amazonaws.com;"',
                ],
            },
            [],
        ),
        (
            {
                "Type": "CAA",
                "ResourceRecords": [
                    # No 3 items
                    "127.0.0.1",
                    # Missing quotes around the value
                    "0 issue amazon.com; henk",
                ],
            },
            [
                ValidationError(
                    (
                        "'127.0.0.1' does not match "
                        "'^(0|128)\\\\s([a-zA-Z0-9]+)\\\\s(\".+\")$'"
                    ),
                    rule=RecordSet(),
                    path=deque(["ResourceRecords", 0]),
                    validator="pattern",
                    schema_path=deque(
                        [
                            "allOf",
                            2,
                            "then",
                            "properties",
                            "ResourceRecords",
                            "items",
                            "pattern",
                        ]
                    ),
                ),
                ValidationError(
                    (
                        "'0 issue amazon.com; henk' does not match "
                        "'^(0|128)\\\\s([a-zA-Z0-9]+)\\\\s(\".+\")$'"
                    ),
                    rule=RecordSet(),
                    path=deque(["ResourceRecords", 1]),
                    validator="pattern",
                    schema_path=deque(
                        [
                            "allOf",
                            2,
                            "then",
                            "properties",
                            "ResourceRecords",
                            "items",
                            "pattern",
                        ]
                    ),
                ),
            ],
        ),
        (
            {
                "Type": "CNAME",
                "ResourceRecords": [
                    "hostname.example.com",
                ],
            },
            [],
        ),
        (
            {
                "Type": "CNAME",
                "ResourceRecords": [
                    "_x2.acm-validations.aws.",
                ],
            },
            [],
        ),
        (
            {
                "Type": "CNAME",
                "ResourceRecords": [
                    "cname1.example.com",
                    "foo√bar",
                ],
            },
            [
                ValidationError(
                    "'foo√bar' is not valid under any of the given schemas",
                    rule=RecordSet(),
                    path=deque(["ResourceRecords", 1]),
                    validator="anyOf",
                    context=deque(
                        [
                            ValidationError(
                                (
                                    "'foo√bar' does not match "
                                    "'^[a-zA-Z0-9\\\\!\"\\\\#\\\\$\\\\%\\\\&\\\\\\'\\\\(\\\\)\\\\*\\\\+\\\\,-\\\\/\\\\:\\\\;\\\\<\\\\=\\\\>\\\\?\\\\@\\\\[\\\\\\\\\\\\]\\\\^\\\\_\\\\`\\\\{\\\\|\\\\}\\\\~\\\\.]+$'"
                                ),  # noqa: E501
                                path=deque([]),
                                validator="pattern",
                                schema_path=deque([0, "pattern"]),
                                rule=RecordSet(),
                            ),
                            ValidationError(
                                (
                                    "'foo√bar' does not match "
                                    "'^.*\\\\.acm-validations\\\\.aws\\\\.?$'"
                                ),
                                path=deque([]),
                                validator="pattern",
                                schema_path=deque([1, "pattern"]),
                                rule=RecordSet(),
                            ),
                        ]
                    ),
                    schema_path=deque(
                        [
                            "allOf",
                            3,
                            "then",
                            "properties",
                            "ResourceRecords",
                            "items",
                            "anyOf",
                        ]
                    ),
                ),
                ValidationError(
                    "expected maximum item count: 1, found: 2",
                    rule=RecordSet(),
                    path=deque(["ResourceRecords"]),
                    validator="maxItems",
                    schema_path=deque(
                        [
                            "allOf",
                            3,
                            "then",
                            "properties",
                            "ResourceRecords",
                            "maxItems",
                        ]
                    ),
                ),
            ],
        ),
        (
            {
                "Type": "CNAME",
                "ResourceRecords": [
                    # No valid domain name
                    "No valid domain name"
                ],
            },
            [
                ValidationError(
                    (
                        "'No valid domain name' is not valid "
                        "under any of the given schemas"
                    ),
                    rule=RecordSet(),
                    path=deque(["ResourceRecords", 0]),
                    validator="anyOf",
                    context=deque(
                        [
                            ValidationError(
                                (
                                    "'No valid domain name' does not match "
                                    "'^[a-zA-Z0-9\\\\!\"\\\\#\\\\$\\\\%\\\\&\\\\\\'\\\\(\\\\)\\\\*\\\\+\\\\,-\\\\/\\\\:\\\\;\\\\<\\\\=\\\\>\\\\?\\\\@\\\\[\\\\\\\\\\\\]\\\\^\\\\_\\\\`\\\\{\\\\|\\\\}\\\\~\\\\.]+$'"  # noqa: E501
                                ),
                                path=deque([]),
                                validator="pattern",
                                schema_path=deque([0, "pattern"]),
                                rule=RecordSet(),
                            ),
                            ValidationError(
                                (
                                    "'No valid domain name' does not match "
                                    "'^.*\\\\.acm-validations\\\\.aws\\\\.?$'"
                                ),
                                path=deque([]),
                                validator="pattern",
                                schema_path=deque([1, "pattern"]),
                                rule=RecordSet(),
                            ),
                        ]
                    ),
                    schema_path=deque(
                        [
                            "allOf",
                            3,
                            "then",
                            "properties",
                            "ResourceRecords",
                            "items",
                            "anyOf",
                        ]
                    ),
                ),
            ],
        ),
        (
            {
                "Type": "MX",
                "ResourceRecords": [
                    "0 mx.example.com",
                    "65535 mx2.example.com",
                ],
            },
            [],
        ),
        (
            {
                "Type": "MX",
                "ResourceRecords": [
                    "127.0.0.1",
                    "10 my domain",
                ],
            },
            [
                ValidationError(
                    (
                        "'127.0.0.1' does not match "
                        "'^([0-9]{1,4}|[1-5][0-9]{4}|6[0-4][0-9]{1-3}|65[0-4][0-9]{1-2}|655[0-2][0-9]|6553[0-5])\\\\s[a-zA-Z0-9\\\\!\"\\\\#\\\\$\\\\%\\\\&\\\\\\'\\\\(\\\\)\\\\*\\\\+\\\\,-\\\\/\\\\:\\\\;\\\\<\\\\=\\\\>\\\\?\\\\@\\\\[\\\\\\\\\\\\]\\\\^\\\\_\\\\`\\\\{\\\\|\\\\}\\\\~\\\\.]+$'"
                    ),
                    rule=RecordSet(),
                    path=deque(["ResourceRecords", 0]),
                    validator="pattern",
                    schema_path=deque(
                        [
                            "allOf",
                            5,
                            "then",
                            "properties",
                            "ResourceRecords",
                            "items",
                            "pattern",
                        ]
                    ),
                ),
                ValidationError(
                    (
                        "'10 my domain' does not match "
                        "'^([0-9]{1,4}|[1-5][0-9]{4}|6[0-4][0-9]{1-3}|65[0-4][0-9]{1-2}|655[0-2][0-9]|6553[0-5])\\\\s[a-zA-Z0-9\\\\!\"\\\\#\\\\$\\\\%\\\\&\\\\\\'\\\\(\\\\)\\\\*\\\\+\\\\,-\\\\/\\\\:\\\\;\\\\<\\\\=\\\\>\\\\?\\\\@\\\\[\\\\\\\\\\\\]\\\\^\\\\_\\\\`\\\\{\\\\|\\\\}\\\\~\\\\.]+$'"
                    ),
                    rule=RecordSet(),
                    path=deque(["ResourceRecords", 1]),
                    validator="pattern",
                    schema_path=deque(
                        [
                            "allOf",
                            5,
                            "then",
                            "properties",
                            "ResourceRecords",
                            "items",
                            "pattern",
                        ]
                    ),
                ),
            ],
        ),
    ],
)
def test_validate(instance, expected, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))
    assert errs == expected, f"Expected {expected} got {errs}"
