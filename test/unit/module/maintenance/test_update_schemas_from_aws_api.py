"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import importlib.util
import json
import re
from pathlib import Path
from test.testlib.testcase import BaseTestCase
from unittest.mock import patch

from botocore.exceptions import ClientError

_REPO_ROOT = Path(__file__).parents[4]

_CEV_REQUIRED_MESSAGE = (
    "A custom engine version is required for SQL Server engine sqlserver-dev-ee. "
    "Create a custom engine version for the template version 15.00.4455.2.v1"
)


def _load_update_schemas_from_aws_api():
    path = _REPO_ROOT / "scripts" / "update_schemas_from_aws_api.py"
    spec = importlib.util.spec_from_file_location("update_schemas_from_aws_api", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _client_error(code, message):
    return ClientError(
        {"Error": {"Code": code, "Message": message}},
        "DescribeOrderableDBInstanceOptions",
    )


class _OrderablePaginator:
    def __init__(self, client):
        self._client = client

    def paginate(self, Engine, EngineVersion):
        self._client.orderable_calls.append((Engine, EngineVersion))
        error = self._client.errors.get((Engine, EngineVersion))
        classes = self._client.orderable.get((Engine, EngineVersion), [])

        def _pages():
            if error is not None:
                raise error
            yield {
                "OrderableDBInstanceOptions": [
                    {"DBInstanceClass": db_instance_class}
                    for db_instance_class in classes
                ]
            }

        return _pages()


class _EngineVersionsPaginator:
    def __init__(self, client):
        self._client = client

    def paginate(self, IncludeAll):
        return iter([{"DBEngineVersions": self._client.engine_versions}])


class _StubRdsClient:
    """Stands in for the boto3 RDS client, recording the calls the script makes."""

    def __init__(self, engine_versions, orderable=None, errors=None):
        self.engine_versions = engine_versions
        self.orderable = orderable or {}
        self.errors = errors or {}
        self.orderable_calls = []

    def get_paginator(self, operation_name):
        if operation_name == "describe_db_engine_versions":
            return _EngineVersionsPaginator(self)
        if operation_name == "describe_orderable_db_instance_options":
            return _OrderablePaginator(self)
        raise AssertionError(f"unexpected operation {operation_name!r}")


def _engine_classes(schema):
    """Map each written schema block back to (engine, version pattern) -> classes."""
    results = {}
    for block in schema["allOf"]:
        engine = block["if"]["properties"]["Engine"]["const"]
        pattern = block["if"]["properties"]["EngineVersion"]["pattern"]
        classes = block["then"]["properties"]["DBInstanceClass"]["enum"]
        results[(engine, pattern)] = classes
    return results


class TestOrderableDbInstanceOptions(BaseTestCase):
    """Collecting orderable DB instance options must survive per-engine refusals."""

    def test_skip_predicate_partitions_supported_engines(self):
        """Only the RDS Custom development engines are left out of collection."""
        module = _load_update_schemas_from_aws_api()

        skipped = [
            engine
            for engine in module._ENGINE_SUPPORTED
            if not module._has_orderable_db_instance_options(engine)
        ]

        self.assertEqual(skipped, ["sqlserver-dev-ee", "sqlserver-dev-se"])
        self.assertEqual(
            len(module._ENGINE_SUPPORTED) - len(skipped),
            21,
            "every other supported engine stays in collection",
        )

    def test_dev_engines_are_never_requested(self):
        """The known CEV-requiring engines are skipped before the API is called."""
        module = _load_update_schemas_from_aws_api()
        client = _StubRdsClient(
            engine_versions=[
                {"Engine": "sqlserver-ee", "EngineVersion": "15.00.4335.1.v1"},
                {"Engine": "sqlserver-dev-ee", "EngineVersion": "15.00.4455.2.v1"},
                {"Engine": "sqlserver-dev-se", "EngineVersion": "15.00.4455.2.v1"},
            ],
            orderable={("sqlserver-ee", "15.00.4335.1.v1"): ["db.m5.large"]},
        )

        with (
            patch.object(module, "rds_client", client),
            patch.object(module, "write_output") as write_output,
        ):
            module.rds_api()

        self.assertEqual(client.orderable_calls, [("sqlserver-ee", "15.00.4335.1.v1")])

        schema = {call.args[1]: call.args[2] for call in write_output.call_args_list}[
            "db_instance_class"
        ]
        self.assertEqual(
            _engine_classes(schema),
            {("sqlserver-ee", r"^(15\.00\..+|15\.00)$"): ["db.m5.large"]},
        )

    def test_custom_engine_version_refusal_does_not_abort_collection(self):
        """A CEV refusal on one engine still leaves every other engine with data."""
        module = _load_update_schemas_from_aws_api()
        client = _StubRdsClient(
            engine_versions=[
                {"Engine": "custom-sqlserver-ee", "EngineVersion": "15.00.4455.2.v1"},
                {"Engine": "mysql", "EngineVersion": "8.0.42"},
                {"Engine": "postgres", "EngineVersion": "17.5"},
            ],
            orderable={
                ("mysql", "8.0.42"): ["db.m5.large"],
                ("postgres", "17.5"): ["db.m5.xlarge"],
            },
            errors={
                ("custom-sqlserver-ee", "15.00.4455.2.v1"): _client_error(
                    "InvalidParameterValue", _CEV_REQUIRED_MESSAGE
                )
            },
        )

        with (
            patch.object(module, "rds_client", client),
            patch.object(module, "write_output") as write_output,
            self.assertLogs("cfnlint", level="WARNING") as logs,
        ):
            module.rds_api()

        self.assertEqual(
            client.orderable_calls,
            [
                ("custom-sqlserver-ee", "15.00.4455.2.v1"),
                ("mysql", "8.0.42"),
                ("postgres", "17.5"),
            ],
        )

        schema = {call.args[1]: call.args[2] for call in write_output.call_args_list}[
            "db_instance_class"
        ]
        collected = _engine_classes(schema)
        self.assertEqual(collected[("mysql", r"^(8\.0\..+|8\.0)$")], ["db.m5.large"])
        self.assertEqual(
            collected[("postgres", r"^(17\.5\..+|17\.5)$")], ["db.m5.xlarge"]
        )

        self.assertEqual(len(logs.output), 1)
        self.assertIn("custom-sqlserver-ee", logs.output[0])
        self.assertIn("15.00.4455.2.v1", logs.output[0])
        self.assertIn(_CEV_REQUIRED_MESSAGE, logs.output[0])

    def test_unexpected_client_errors_still_abort_collection(self):
        """Credential, throttling and service errors are not swallowed."""
        module = _load_update_schemas_from_aws_api()
        for code in [
            "AccessDenied",
            "AccessDeniedException",
            "ExpiredToken",
            "InternalFailure",
            "ThrottlingException",
            "UnrecognizedClientException",
        ]:
            with self.subTest(code=code):
                client = _StubRdsClient(
                    engine_versions=[{"Engine": "mysql", "EngineVersion": "8.0.42"}],
                    errors={("mysql", "8.0.42"): _client_error(code, "nope")},
                )
                with (
                    patch.object(module, "rds_client", client),
                    patch.object(module, "write_output"),
                    self.assertRaises(ClientError) as raised,
                ):
                    module.rds_api()

                self.assertEqual(raised.exception.response["Error"]["Code"], code)

    def test_db_instance_class_schema_round_trips_recorded_data(self):
        """Recorded instance classes regenerate the committed schema byte for byte."""
        module = _load_update_schemas_from_aws_api()
        committed_path = (
            _REPO_ROOT
            / "src/cfnlint/data/schemas/extensions/aws_rds_dbinstance"
            / "db_instance_class.json"
        )
        committed = json.loads(committed_path.read_text(encoding="utf-8"))

        results = {}
        for block in committed["allOf"]:
            engine = block["if"]["properties"]["Engine"]["const"]
            pattern = block["if"]["properties"]["EngineVersion"]["pattern"]
            version = ".".join(
                re.match(r"^\^\((.+?)\\\.(.+?)\\\.\.\+\|", pattern).groups()
            )
            results.setdefault(engine, {})[version] = {
                "EngineVersions": set([version]),
                "DBInstanceClass": set(
                    block["then"]["properties"]["DBInstanceClass"]["enum"]
                ),
            }

        with patch.object(module, "write_output") as write_output:
            module.write_db_instance_version_dbinstanceclass(results)

        regenerated = write_output.call_args.args[2]
        regenerated["description"] = "Automatically updated using aws api"
        self.assertEqual(
            json.dumps(regenerated, indent=1, sort_keys=True, separators=(",", ": "))
            + "\n",
            committed_path.read_text(encoding="utf-8"),
        )
