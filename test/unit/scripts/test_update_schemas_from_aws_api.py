"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import importlib.util
import sys
import types
from pathlib import Path

import pytest

# The generator script is a maintenance script, not part of the package:
# it imports boto3 at module level, but boto3 is not a test dependency.
# Stub it only when it is not installed, so these tests run in the
# normal test environment without adding a dependency.
try:
    import boto3  # noqa: F401
except ImportError:  # pragma: no cover - depends on the test environment
    boto3 = types.ModuleType("boto3")
    session = types.ModuleType("boto3.session")

    class _Session:
        def client(self, *args, **kwargs):
            return object()

    session.Session = _Session
    boto3.session = session
    sys.modules["boto3"] = boto3
    sys.modules["boto3.session"] = session

    botocore = types.ModuleType("botocore")
    botocore_client = types.ModuleType("botocore.client")

    class _Config:
        def __init__(self, *args, **kwargs):
            pass

    botocore_client.Config = _Config
    botocore.client = botocore_client
    sys.modules["botocore"] = botocore
    sys.modules["botocore.client"] = botocore_client

_SCRIPT = Path(__file__).parents[3] / "scripts" / "update_schemas_from_aws_api.py"
_spec = importlib.util.spec_from_file_location(
    "update_schemas_from_aws_api", _SCRIPT
)
_script = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_script)


def _deprecated_enums(captured, engine):
    """Return the deprecated EngineVersion enums for one engine."""
    enums = []
    for _resource, _filename, schema in captured:
        for entry in schema["allOf"]:
            properties = entry["if"]["properties"]
            if properties.get("Engine", {}).get("const") != engine:
                continue
            enums.append(properties["EngineVersion"]["enum"])
    return enums


@pytest.mark.parametrize(
    "available_versions,prefix,expected",
    [
        # An available release under the prefix keeps it usable.
        ({"16.11": {}}, "16", True),
        # Exact match counts as available.
        ({"16": {}}, "16", True),
        # The dot boundary matters: 160 is not under prefix 16.
        ({"160.1": {}}, "16", False),
        # No available version at all.
        ({}, "16", False),
        # A different major is unrelated.
        ({"15.4": {}}, "16", False),
    ],
)
def test_has_available_version(available_versions, prefix, expected):
    assert _script._has_available_version(available_versions, prefix) == expected


def test_write_db_instance_deprecated_prefixes(monkeypatch):
    captured = []
    monkeypatch.setattr(
        _script, "write_output", lambda *args: captured.append(args)
    )
    # https://github.com/aws-cloudformation/cfn-lint/issues/4840
    # postgres 16.1 is deprecated but 16.11 is still available, so the
    # shortened prefix 16 must not be marked deprecated. postgres 15 has
    # no available release left, so prefix 15 stays deprecated.
    _script.write_db_instance_deprecated(
        {"postgres": {"16.1": {}, "15.4": {}}},
        {"postgres": {"16.11": {}}},
    )
    (enum,) = _deprecated_enums(captured, "postgres")
    assert "16" not in enum
    assert "15" in enum
    assert "16.1" in enum
    assert "15.4" in enum


def test_write_db_instance_deprecated_aurora_mysql_prefix(monkeypatch):
    captured = []
    monkeypatch.setattr(
        _script, "write_output", lambda *args: captured.append(args)
    )
    _script.write_db_instance_deprecated(
        {"aurora-mysql": {"8.0.36": {}}},
        {"aurora-mysql": {"8.0.39": {}}},
    )
    (enum,) = _deprecated_enums(captured, "aurora-mysql")
    assert "8.0" not in enum
    assert "8.0.36" in enum

    captured.clear()
    _script.write_db_instance_deprecated(
        {"aurora-mysql": {"8.0.36": {}}},
        {"aurora-mysql": {}},
    )
    (enum,) = _deprecated_enums(captured, "aurora-mysql")
    assert "8.0" in enum
    assert "8.0.36" in enum


def test_write_db_cluster_deprecated_prefixes(monkeypatch):
    captured = []
    monkeypatch.setattr(
        _script, "write_output", lambda *args: captured.append(args)
    )
    # aurora-postgresql 16.1 is deprecated but 16.2 is still available,
    # so the major-only prefix 16 must not be marked deprecated.
    _script.write_db_cluster_deprecated(
        {"aurora-postgresql": {"16.1": {}}},
        {"aurora-postgresql": {"16.2": {}}},
    )
    (enum,) = _deprecated_enums(captured, "aurora-postgresql")
    assert "16" not in enum
    assert "16.1" in enum

    captured.clear()
    _script.write_db_cluster_deprecated(
        {"aurora-postgresql": {"16.1": {}}},
        {"aurora-postgresql": {}},
    )
    (enum,) = _deprecated_enums(captured, "aurora-postgresql")
    assert "16" in enum
    assert "16.1" in enum
