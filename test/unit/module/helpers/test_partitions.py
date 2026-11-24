"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest
import regex as re

from cfnlint.helpers import PARTITIONS, REGIONS, get_partition, get_url_suffix

# Partition and DNS suffix per region as published in botocore's endpoints.json
_EXPECTED = {
    "us-east-1": ("aws", "amazonaws.com"),
    "eu-west-1": ("aws", "amazonaws.com"),
    "us-gov-west-1": ("aws-us-gov", "amazonaws.com"),
    "us-gov-east-1": ("aws-us-gov", "amazonaws.com"),
    "cn-north-1": ("aws-cn", "amazonaws.com.cn"),
    "cn-northwest-1": ("aws-cn", "amazonaws.com.cn"),
    "us-iso-east-1": ("aws-iso", "c2s.ic.gov"),
    "us-iso-west-1": ("aws-iso", "c2s.ic.gov"),
    "us-isob-east-1": ("aws-iso-b", "sc2s.sgov.gov"),
    "us-isob-west-1": ("aws-iso-b", "sc2s.sgov.gov"),
    "eu-isoe-west-1": ("aws-iso-e", "cloud.adc-e.uk"),
    "us-isof-east-1": ("aws-iso-f", "csp.hci.ic.gov"),
    "us-isof-south-1": ("aws-iso-f", "csp.hci.ic.gov"),
    "eusc-de-east-1": ("aws-eusc", "amazonaws.eu"),
}

# botocore's regionRegex for the commercial partition
_COMMERCIAL = re.compile(r"^(us|eu|ap|sa|ca|me|af|il|mx)\-\w+\-\d+$")


@pytest.mark.parametrize("region,expected", list(_EXPECTED.items()))
def test_partition_and_suffix(region, expected):
    assert (get_partition(region), get_url_suffix(region)) == expected


def test_unknown_region_falls_back_to_commercial():
    assert get_partition("xx-fake-1") == "aws"
    assert get_url_suffix("xx-fake-1") == "amazonaws.com"


@pytest.mark.parametrize("region", REGIONS)
def test_every_supported_region_has_a_known_partition(region):
    # A region that is not commercial must be matched by the table rather than
    # falling back to aws
    matched = any(pattern.match(region) for pattern, _, _ in PARTITIONS)
    assert matched or _COMMERCIAL.match(region), region
