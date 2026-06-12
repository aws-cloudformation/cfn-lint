"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import fnmatch
import json
import os
import pathlib
from typing import Any, List
from unittest import TestCase

import pytest
import regex as re

import cfnlint
from cfnlint.helpers import ensure_list, load_plugins
from cfnlint.jsonschema import StandardValidator, ValidationError
from cfnlint.schema.resolver import RefResolutionError, RefResolver


@pytest.mark.data
class TestSchemaFiles(TestCase):
    """Test schema files"""

    _TEMPLATE_KEYWORDS: List[str] = [
        "*",
        "Conditions",
        "Description",
        "Mappings",
        "Metadata",
        "Metadata/AWS::CloudFormation::Interface",
        "Metadata/cfn-lint",
        "Outputs",
        "Outputs/*",
        "Outputs/*/Condition",
        "Outputs/*/Export/Name",
        "Outputs/*/Value",
        "Parameters",
        "Parameters/*",
        "Parameters/*/AllowedPattern",
        "Parameters/*/Type",
        "Resources",
        "Resources/*",
        "Resources/*/Condition",
        "Resources/*/CreationPolicy",
        "Resources/*/DeletionPolicy",
        "Resources/*/DependsOn",
        "Resources/*/DependsOn/*",
        "Resources/*/Metadata",
        "Resources/*/Metadata/AWS::CloudFormation::Init",
        "Resources/*/Type",
        "Resources/*/UpdatePolicy",
        "Resources/*/UpdateReplacePolicy",
        "Rules",
        "Rules/*/Assertions/*/Assert",
        "Rules/*/RuleCondition",
        "Transform",
    ]

    def setUp(self) -> None:
        schema_path = os.path.join(os.path.dirname(cfnlint.__file__), "data", "schemas")
        self.paths = {
            "extensions": os.path.join(schema_path, "extensions"),
            "providers": os.path.join(schema_path, "providers"),
            "resources": os.path.join(schema_path, "resources"),
            "other": os.path.join(schema_path, "other"),
            "fixtures": os.path.join(
                os.path.dirname(__file__),
                "..",
                "fixtures",
                "schemas",
                "providers",
            ),
        }
        filename = os.path.join(
            self.paths["fixtures"], "..", "json_schema", "draft7.json"
        )
        with open(filename, "r") as fh:
            d = json.load(fh)
            self.schema_draft7 = d

        super().setUp()

    def get_files(self, dir):
        for dirpath, _, filenames in os.walk(dir):
            for filename in fnmatch.filter(filenames, "*.json"):
                yield dirpath, filename

    def pattern(self, validator, patrn, instance, schema):
        try:
            re.compile(patrn)
        except Exception:
            yield ValidationError(f"Pattern doesn't compile: {patrn}")

    def validate_basic_schema_details(
        self, schema_resolver: RefResolver, filepath: str
    ):
        """
        Validate that readOnly, writeOnly, etc are valid
        """
        sections = [
            "readOnlyProperties",
            "writeOnlyProperties",
            "conditionalCreateOnlyProperties",
            "nonPublicProperties",
            "nonPublicDefinitions",
            "createOnlyProperties",
            "deprecatedProperties",
            "primaryIdentifier",
        ]
        for section in sections:
            for prop in schema_resolver.referrer.get(section, []):
                try:
                    self.assertIsNotNone(schema_resolver.resolve_cfn_pointer(prop))
                except RefResolutionError:
                    self.fail(f"Can't find prop {prop} for {section} in {filepath}")

    def cfn_lint(self, validator, _, keywords, schema):
        pass

    def test_other_specs(self):
        """Test data file formats"""

        store = {}
        dir = self.paths["fixtures"]
        for dirpath, filename in self.get_files(dir):
            with open(os.path.join(dirpath, filename), "r", encoding="utf8") as fh:
                store[filename] = json.load(fh)

        resolver = RefResolver.from_schema(store["cfnlint.schema.v1.json"], store=store)

        validator = (
            StandardValidator({})
            .extend(
                validators={
                    "cfnLint": self.cfn_lint,
                    "pattern": self.pattern,
                },
            )(schema=store["cfnlint.schema.v1.json"])
            .evolve(resolver=resolver)
        )

        for dir_name in ["extensions", "other"]:
            dir = self.paths[dir_name]

            for dirpath, filename in self.get_files(dir):
                with open(os.path.join(dirpath, filename), "r", encoding="utf8") as fh:
                    d = json.load(fh)
                    errs = list(validator.iter_errors(d))
                    self.assertListEqual(
                        errs, [], f"Error with {dirpath}/{filename}: {errs}"
                    )
                    schema_resolver = RefResolver(d)
                    self.validate_basic_schema_details(
                        schema_resolver, f"{dirpath}/{filename}"
                    )

    def _resolve_path_in_schema(
        self, path_parts: list[str], obj: Any, resolver: RefResolver, refs: list[str]
    ) -> bool:
        """Check if a property path resolves within a schema object."""
        if not path_parts:
            return True

        if not isinstance(obj, dict):
            return False

        if "$ref" in obj:
            ref = obj["$ref"]
            if ref in refs:
                return False
            _, resolved = resolver.resolve(ref)
            return self._resolve_path_in_schema(
                path_parts, resolved, resolver, refs + [ref]
            )

        part = path_parts[0]
        remaining = path_parts[1:]

        if part == "*":
            if "items" in obj:
                return self._resolve_path_in_schema(
                    remaining, obj["items"], resolver, refs
                )
            return False

        if part in obj.get("properties", {}):
            return self._resolve_path_in_schema(
                remaining, obj["properties"][part], resolver, refs
            )

        # Accept paths into unstructured objects (type includes "object"
        # but no properties defined — e.g. IAM PolicyDocument)
        if "object" in ensure_list(obj.get("type", [])):
            return True

        return False

    def test_x_keywords(self):
        """Test that all rule keyword paths resolve against the schemas"""
        provider_file = os.path.join(self.paths["providers"], "us-east-1.json")
        try:
            with open(provider_file, "r", encoding="utf-8") as f:
                resource_types = json.load(f)
        except FileNotFoundError:
            self.skipTest(
                "Schemas not downloaded — run cfn-lint --update-specs --force"
            )

        # Collect cfnLint keywords from extension/other schemas
        cfnlint_keywords: set[str] = set()
        for dir_name in ["extensions", "other"]:
            dir = self.paths[dir_name]
            for dirpath, filename in self.get_files(dir):
                with open(os.path.join(dirpath, filename), "r", encoding="utf8") as fh:
                    d = json.load(fh)
                    for kw in ensure_list(d.get("cfnLint", [])):
                        cfnlint_keywords.add(kw)

        valid_keywords: set[str] = set(self._TEMPLATE_KEYWORDS) | cfnlint_keywords
        valid_keywords.add("cfnParameter")

        root_dir = pathlib.Path(__file__).parent.parent.parent / "src/cfnlint/rules"
        rules = load_plugins(
            str(root_dir),
            "CfnLintKeyword",
            "cfnlint.rules.jsonschema.CfnLintKeyword",
        )
        rules.extend(
            load_plugins(
                str(root_dir),
                "CfnLintJsonSchema",
                "cfnlint.rules.jsonschema.CfnLintJsonSchema",
            )
        )

        # Cache loaded schemas by resource type
        schema_cache: dict[str, Any] = {}

        for rule in rules:
            for keyword in rule.keywords:
                if keyword in valid_keywords:
                    continue

                parts = keyword.split("/")

                # Handle Resources/AWS::X::Y/Properties/... or
                # AWS::X::Y/Properties/... (shorthand without Resources/ prefix)
                if parts[0] == "Resources" and len(parts) >= 3:
                    resource_type = parts[1]
                    prop_parts = parts[3:]
                elif "::" in parts[0] and len(parts) >= 2:
                    resource_type = parts[0]
                    prop_parts = parts[2:]
                else:
                    self.fail(f"{keyword} not found")

                if resource_type not in resource_types:
                    self.fail(
                        f"{keyword} references unknown resource type {resource_type}"
                    )

                if not prop_parts:
                    continue

                if resource_type not in schema_cache:
                    schema_hash = resource_types[resource_type]
                    schema_file = os.path.join(
                        self.paths["resources"], f"{schema_hash}.json"
                    )
                    with open(schema_file, "r", encoding="utf-8") as f:
                        schema_cache[resource_type] = json.load(f)

                schema = schema_cache[resource_type]
                resolver = RefResolver(schema)
                resolved = self._resolve_path_in_schema(
                    prop_parts, schema, resolver, []
                )
                self.assertTrue(
                    resolved,
                    f"{keyword} does not resolve in {resource_type} schema",
                )
