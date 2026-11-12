"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.rules.templates.InlineLimitSize import InlineLimitSize
from cfnlint.template import Template

_TEMPLATE = {"Resources": {"Topic": {"Type": "AWS::SNS::Topic"}}}


@pytest.fixture(scope="module")
def rule():
    rule = InlineLimitSize()
    yield rule


def _write_template(path, size, pad):
    """Write a template file of exactly `size` bytes, padded with `pad`"""
    prefix = "Resources:\n  Topic:\n    Type: AWS::SNS::Topic\n# "
    count = (size - len(prefix.encode("utf-8"))) // len(pad.encode("utf-8"))
    body = prefix + pad * count
    body += "x" * (size - len(body.encode("utf-8")))
    path.write_bytes(body.encode("utf-8"))
    assert path.stat().st_size == size

    return str(path)


@pytest.mark.parametrize(
    "size,pad,expected_count",
    [
        # Valid: exactly at the inline limit
        (51_200, "x", 0),
        # Invalid: one byte past the inline limit
        (51_201, "x", 1),
        # Invalid: multi-byte characters count by byte, as the file is measured
        (51_201, "é", 1),
        # Invalid: at the S3 limit, which still needs S3
        (1_000_000, "x", 1),
        # Valid here: past the S3 limit, which E1002 reports
        (1_000_001, "x", 0),
    ],
)
def test_file_size(size, pad, expected_count, rule, tmp_path):
    filename = _write_template(tmp_path / "template.yaml", size, pad)
    matches = rule.match(Template(filename, _TEMPLATE))

    assert len(matches) == expected_count, (
        f"Expected {expected_count} matches got {len(matches)}"
    )
    if expected_count:
        assert matches[0].message == (
            "The template file is larger than 51200 bytes, the limit for a "
            "template body passed inline. Upload it to S3 and deploy it with "
            "'TemplateURL' or '--s3-bucket'"
        )


def test_template_from_stdin(rule):
    assert rule.match(Template(None, _TEMPLATE)) == []


def test_filename_not_a_file(rule, tmp_path):
    assert rule.match(Template(str(tmp_path), _TEMPLATE)) == []
