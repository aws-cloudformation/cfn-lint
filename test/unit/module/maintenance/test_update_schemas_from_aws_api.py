"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import importlib.util
from pathlib import Path
from test.testlib.testcase import BaseTestCase
from unittest.mock import patch

_ENGINE_VERSIONS = [
    {"Engine": "mysql", "EngineVersion": "8.0.42", "Status": "available"},
    {"Engine": "mysql", "EngineVersion": "5.7.44", "Status": "deprecated"},
    {
        "Engine": "sqlserver-dev-ee",
        "EngineVersion": "15.00.4455.2.v1",
        "Status": "requires-custom-engine-version",
    },
    {"Engine": "postgres", "EngineVersion": "17.5"},
]


def _load_update_schemas_from_aws_api():
    path = Path(__file__).parents[4] / "scripts" / "update_schemas_from_aws_api.py"
    spec = importlib.util.spec_from_file_location("update_schemas_from_aws_api", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class _EngineVersionsPaginator:
    def __init__(self, client):
        self._client = client

    def paginate(self, IncludeAll):
        return iter([{"DBEngineVersions": self._client.engine_versions}])


class _OrderablePaginator:
    def __init__(self, client):
        self._client = client

    def paginate(self, Engine, EngineVersion):
        self._client.orderable_calls.append((Engine, EngineVersion))
        return iter([{"OrderableDBInstanceOptions": []}])


class _StubRdsClient:
    """Stands in for the boto3 RDS client, recording the calls the script makes."""

    def __init__(self, engine_versions):
        self.engine_versions = engine_versions
        self.orderable_calls = []

    def get_paginator(self, operation_name):
        if operation_name == "describe_db_engine_versions":
            return _EngineVersionsPaginator(self)
        if operation_name == "describe_orderable_db_instance_options":
            return _OrderablePaginator(self)
        raise AssertionError(f"unexpected operation {operation_name!r}")


def _run_rds_api(module, engine_versions):
    client = _StubRdsClient(engine_versions)
    with (
        patch.object(module, "rds_client", client),
        patch.object(module, "write_db_cluster"),
        patch.object(module, "write_db_cluster_deprecated"),
        patch.object(module, "write_db_instance") as write_db_instance,
        patch.object(module, "write_db_instance_deprecated") as write_deprecated,
        patch.object(module, "write_db_instance_version_dbinstanceclass"),
    ):
        module.rds_api()

    return (
        client,
        write_db_instance.call_args.args[0],
        write_deprecated.call_args.args[0],
    )


class TestRdsEngineVersionStatus(BaseTestCase):
    """DescribeDBEngineVersions returns three statuses, not two."""

    def test_requires_custom_engine_version_is_not_collected(self):
        """Only available versions reach DescribeOrderableDBInstanceOptions."""
        module = _load_update_schemas_from_aws_api()

        client, _, _ = _run_rds_api(module, _ENGINE_VERSIONS)

        self.assertEqual(
            client.orderable_calls,
            [("mysql", "8.0.42"), ("postgres", "17.5")],
        )

    def test_available_and_deprecated_versions_are_unchanged(self):
        """Every status still reaches the enums, and only deprecated is deprecated."""
        module = _load_update_schemas_from_aws_api()

        _, results, deprecated_results = _run_rds_api(module, _ENGINE_VERSIONS)

        self.assertEqual(
            results,
            {
                "mysql": {"8.0.42": {}, "5.7.44": {}},
                "sqlserver-dev-ee": {"15.00.4455.2.v1": {}},
                "postgres": {"17.5": {}},
            },
        )
        self.assertEqual(deprecated_results, {"mysql": {"5.7.44": {}}})
