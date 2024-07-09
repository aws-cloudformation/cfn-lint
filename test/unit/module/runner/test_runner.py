"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from unittest.mock import patch

import pytest

from cfnlint.config import ConfigMixIn
from cfnlint.runner import PROVIDER_SCHEMA_MANAGER, Runner
from cfnlint.schema import Schema


def patch_registry(path):
    PROVIDER_SCHEMA_MANAGER._registry_schemas = {
        "Foo::Bar::MODULE": Schema(
            {
                "typeName": "Foo::Bar::MODULE",
                "properties": {
                    "Foo": {
                        "type": "string",
                    },
                    "Bar": {
                        "type": "string",
                    },
                },
                "primaryIdentifiers": [],
            }
        )
    }


def patch_schema(path, regions):
    PROVIDER_SCHEMA_MANAGER._registry_schemas["Foo::Bar::MODULE"].schema[
        "primaryIdentifiers"
    ] = ["/properties/Foo"]


@pytest.mark.parametrize(
    "name,registry_path,patch_path,expected",
    [
        (
            "Test no changes to the schema",
            None,
            None,
            False,
        ),
        (
            "Test patching registry resources",
            "path/to/registry/schemas",
            "patch.json",
            False,
        ),
        (
            "Test registry resource with no patching",
            "path/to/registry/schemas",
            None,
            False,
        ),
    ],
)
def test_init_schemas(name, registry_path, patch_path, expected):
    params = []
    if registry_path:
        params.extend(["--registry-schemas", "path/to/registry/schemas"])
    if patch_path:
        params.extend(["--override-spec", "patch.json"])
    config = ConfigMixIn(params)

    with patch.object(
        PROVIDER_SCHEMA_MANAGER, "load_registry_schemas", new=patch_registry
    ):
        with patch.object(PROVIDER_SCHEMA_MANAGER, "patch", new=patch_schema):
            Runner(config)

            if registry_path:
                assert "Foo::Bar::MODULE" in PROVIDER_SCHEMA_MANAGER.get_resource_types(
                    "us-east-1"
                )
                schema = PROVIDER_SCHEMA_MANAGER.get_resource_schema(
                    "us-east-1", "Foo::Bar::MODULE"
                )
                if patch_path:
                    assert schema.schema["primaryIdentifiers"] == ["/properties/Foo"]
                else:
                    assert schema.schema["primaryIdentifiers"] == []
            else:
                assert (
                    "Foo::Bar::MODULE"
                    not in PROVIDER_SCHEMA_MANAGER.get_resource_types("us-east-1")
                )

    PROVIDER_SCHEMA_MANAGER._registry_schemas = {}
    PROVIDER_SCHEMA_MANAGER.reset()
