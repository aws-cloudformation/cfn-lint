"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from pathlib import Path

import pytest

from cfnlint.api import lint
from cfnlint.jsonschema import CfnTemplateValidator
from cfnlint.rules.resources.iam.ResourceSqsPolicy import ResourceSqsPolicy


@pytest.mark.parametrize(
    "filename,expected",
    [
        ("test/fixtures/templates/good/resources/sqs/queue_policy.yaml", []),
        (
            "test/fixtures/templates/bad/resources/sqs/queue_policy.yaml",
            [("E3515", 23), ("E3515", 45), ("E3515", 60), ("E3515", 69)],
        ),
    ],
)
def test_templates(filename, expected):
    # The rule is driven by the resource schema, so run the whole rule set
    matches = lint(Path(filename).read_text())

    assert [(m.rule.id, m.linenumber) for m in matches] == expected, matches


def _policy(resource_key: str, resource):
    return {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"AWS": "arn:aws:iam::123456789012:root"},
                "Action": "sqs:SendMessage",
                resource_key: resource,
            }
        ],
    }


_QUEUE_A = "arn:aws:sqs:us-east-1:123456789012:queue-a"
_QUEUE_B = "arn:aws:sqs:us-east-1:123456789012:queue-b"


@pytest.mark.parametrize(
    "name,policy,expected",
    [
        ("Resource as a string", _policy("Resource", _QUEUE_A), []),
        ("Resource as a one item list", _policy("Resource", [_QUEUE_A]), []),
        ("Resource as a wildcard", _policy("Resource", "*"), []),
        (
            "Resource with two queues",
            _policy("Resource", [_QUEUE_A, _QUEUE_B]),
            [
                (
                    "expected maximum item count: 1, found: 2",
                    ["Statement", 0, "Resource"],
                )
            ],
        ),
        ("NotResource as a string", _policy("NotResource", _QUEUE_A), []),
        ("NotResource as a one item list", _policy("NotResource", [_QUEUE_A]), []),
        (
            "NotResource with two queues",
            _policy("NotResource", [_QUEUE_A, _QUEUE_B]),
            [
                (
                    "expected maximum item count: 1, found: 2",
                    ["Statement", 0, "NotResource"],
                )
            ],
        ),
        (
            "Resource and Statement as an object",
            {
                "Version": "2012-10-17",
                "Statement": _policy("Resource", [_QUEUE_A, _QUEUE_B])["Statement"][
                    0
                ],
            },
            [
                (
                    "expected maximum item count: 1, found: 2",
                    ["Statement", "Resource"],
                )
            ],
        ),
        (
            "Generic resource policy checks still apply",
            {"Version": "2012-10-18"},
            [
                (
                    "'2012-10-18' is not one of ['2008-10-17', '2012-10-17']",
                    ["Version"],
                ),
                ("'Statement' is a required property", []),
            ],
        ),
    ],
)
def test_validate(name, policy, expected):
    rule = ResourceSqsPolicy()
    errs = list(
        rule.validate(
            validator=CfnTemplateValidator({}),
            policy_type=None,
            policy=policy,
            schema={},
        )
    )

    assert sorted((e.message, list(e.path)) for e in errs) == sorted(expected), (
        f"For test {name!r} got {errs!r}"
    )
