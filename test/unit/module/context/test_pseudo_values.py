"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.context.context import _get_pseudo_value_by_region


@pytest.mark.parametrize(
    "region,partition,suffix",
    [
        ("us-east-1", "aws", "amazonaws.com"),
        ("cn-north-1", "aws-cn", "amazonaws.com.cn"),
        ("us-iso-east-1", "aws-iso", "c2s.ic.gov"),
        ("eusc-de-east-1", "aws-eusc", "amazonaws.eu"),
    ],
)
def test_pseudo_values_follow_the_partition(region, partition, suffix):
    assert _get_pseudo_value_by_region("AWS::Partition", region) == partition
    assert _get_pseudo_value_by_region("AWS::URLSuffix", region) == suffix
    assert _get_pseudo_value_by_region("AWS::StackId", region).startswith(
        f"arn:{partition}:cloudformation:{region}:"
    )
    assert _get_pseudo_value_by_region("AWS::NotificationARNs", region) == [
        f"arn:{partition}:sns:{region}:123456789012:notification"
    ]
