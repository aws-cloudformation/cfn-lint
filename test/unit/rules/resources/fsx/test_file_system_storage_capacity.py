"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint.rules.resources.fsx.FileSystemStorageCapacity import (
    FileSystemStorageCapacity,
)


@pytest.fixture(scope="module")
def rule():
    rule = FileSystemStorageCapacity()
    yield rule


@pytest.mark.parametrize(
    "instance,expected_count,expected_message",
    [
        # Valid: no FileSystemType (e.g. creating from a backup)
        (
            {"StorageCapacity": 100},
            0,
            None,
        ),
        # Valid: no StorageCapacity
        (
            {"FileSystemType": "LUSTRE"},
            0,
            None,
        ),
        # Valid: wrong type is handled elsewhere
        (
            [],
            0,
            None,
        ),
        # Valid: Windows at the minimum and maximum
        (
            {"FileSystemType": "WINDOWS", "StorageCapacity": 32},
            0,
            None,
        ),
        (
            {"FileSystemType": "WINDOWS", "StorageCapacity": 65536},
            0,
            None,
        ),
        # Valid: OpenZFS at the minimum and maximum
        (
            {"FileSystemType": "OPENZFS", "StorageCapacity": 64},
            0,
            None,
        ),
        (
            {"FileSystemType": "OPENZFS", "StorageCapacity": 524288},
            0,
            None,
        ),
        # Valid: Lustre at the minimum
        (
            {"FileSystemType": "LUSTRE", "StorageCapacity": 1200},
            0,
            None,
        ),
        # Valid: Lustre above the stale 65536 cap (the #4706 scenario)
        (
            {"FileSystemType": "LUSTRE", "StorageCapacity": 460800},
            0,
            None,
        ),
        # Valid: SCRATCH_1 Lustre at the minimum (all Lustre types share min 1200)
        (
            {
                "FileSystemType": "LUSTRE",
                "LustreConfiguration": {"DeploymentType": "SCRATCH_1"},
                "StorageCapacity": 1200,
            },
            0,
            None,
        ),
        # Valid: PERSISTENT_1 Lustre above the stale 65536 cap
        (
            {
                "FileSystemType": "LUSTRE",
                "LustreConfiguration": {"DeploymentType": "PERSISTENT_1"},
                "StorageCapacity": 100800,
            },
            0,
            None,
        ),
        # Valid: ONTAP at the minimum and well above the stale cap
        (
            {"FileSystemType": "ONTAP", "StorageCapacity": 1024},
            0,
            None,
        ),
        (
            {"FileSystemType": "ONTAP", "StorageCapacity": 200000},
            0,
            None,
        ),
        # Invalid: Windows below the minimum
        (
            {"FileSystemType": "WINDOWS", "StorageCapacity": 16},
            1,
            "16 is less than the minimum of 32 for 'WINDOWS' file systems",
        ),
        # Invalid: Windows above the maximum
        (
            {"FileSystemType": "WINDOWS", "StorageCapacity": 100000},
            1,
            "100000 is greater than the maximum of 65536 for 'WINDOWS' file systems",
        ),
        # Invalid: Lustre below the minimum
        (
            {"FileSystemType": "LUSTRE", "StorageCapacity": 1000},
            1,
            "1000 is less than the minimum of 1200 for 'LUSTRE' file systems",
        ),
        # Invalid: SCRATCH_1 Lustre below the minimum
        (
            {
                "FileSystemType": "LUSTRE",
                "LustreConfiguration": {"DeploymentType": "SCRATCH_1"},
                "StorageCapacity": 1000,
            },
            1,
            "1000 is less than the minimum of 1200 for 'LUSTRE' file systems",
        ),
        # Invalid: PERSISTENT_1 Lustre below the minimum
        (
            {
                "FileSystemType": "LUSTRE",
                "LustreConfiguration": {"DeploymentType": "PERSISTENT_1"},
                "StorageCapacity": 800,
            },
            1,
            "800 is less than the minimum of 1200 for 'LUSTRE' file systems",
        ),
        # Invalid: OpenZFS below the minimum
        (
            {"FileSystemType": "OPENZFS", "StorageCapacity": 32},
            1,
            "32 is less than the minimum of 64 for 'OPENZFS' file systems",
        ),
        # Invalid: OpenZFS above the maximum
        (
            {"FileSystemType": "OPENZFS", "StorageCapacity": 600000},
            1,
            "600000 is greater than the maximum of 524288 for 'OPENZFS' file systems",
        ),
        # Invalid: ONTAP below the minimum
        (
            {"FileSystemType": "ONTAP", "StorageCapacity": 1000},
            1,
            "1000 is less than the minimum of 1024 for 'ONTAP' file systems",
        ),
    ],
)
def test_validate(instance, expected_count, expected_message, rule, validator):
    errs = list(rule.validate(validator, "", instance, {}))

    assert len(errs) == expected_count, (
        f"Expected {expected_count} errors got {len(errs)}: {errs!r}"
    )
    if expected_message:
        assert errs[0].message == expected_message
