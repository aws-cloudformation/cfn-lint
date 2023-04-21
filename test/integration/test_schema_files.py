"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import fnmatch
import json
import os
import re
from typing import Any, Generator
from unittest import TestCase

import jsonschema
from jsonschema._utils import ensure_list, extras_msg, find_additional_properties
from jsonschema.validators import extend

import cfnlint
import cfnlint.core
from cfnlint.helpers import REGIONS


class TestSchemaFiles(TestCase):
    """Test schema files"""

    used_cfn_schemas = []

    def setUp(self) -> None:
        self.paths = {
            "extensions": os.path.join(
                os.path.dirname(cfnlint.__file__), "data", "schemas", "extensions"
            ),
            "providers": os.path.join(
                os.path.dirname(cfnlint.__file__), "data", "schemas", "providers"
            ),
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

    def cfn_schema(self, validator, cSs, schemas, schema):
        schemas = ensure_list(schemas)
        for schema in schemas:
            filename = os.path.join(
                self.paths["extensions"], *"".join([schema, ".json"]).split("/")
            )
            if not os.path.exists(filename):
                yield jsonschema.ValidationError(f"CfnSchema doesn't exist: {filename}")

            if filename in self.used_cfn_schemas:
                self.used_cfn_schemas.remove(filename)

    def test_1_cfn_schemas(self):
        """Test CFN schemas"""
        filename = os.path.join(self.paths["extensions"], "json_schema", "draft7.json")

        for dirpath, filename in self.get_files(self.paths["extensions"]):
            filename = os.path.join(dirpath, filename)
            with open(filename, "r") as fh:
                d = json.load(fh)
                self.schema_draft7 = d
                self.used_cfn_schemas.append(filename)

    def test_2_data_module_specs(self):
        """Test data file formats"""

        store = {}
        dir = self.paths["fixtures"]
        for dirpath, filename in self.get_files(dir):
            with open(os.path.join(dirpath, filename), "r", encoding="utf8") as fh:
                store[filename] = json.load(fh)

        resolver = jsonschema.RefResolver.from_schema(
            store["provider.definition.schema.v1.json"], store=store
        )

        validator = extend(
            validator=jsonschema.Draft7Validator,
            validators={
                "cfnSchema": self.cfn_schema,
                "cfnRegionalSchema": self.cfn_schema,
            },
        )(schema=store["provider.definition.schema.v1.json"]).evolve(resolver=resolver)

        validator.VALIDATORS["cfnSchema"] = self.cfn_schema

        for region in REGIONS:
            dir = os.path.join(
                self.paths["providers"],
                region.replace("-", "_"),
            )

            for dirpath, filename in self.get_files(dir):
                with open(os.path.join(dirpath, filename), "r", encoding="utf8") as fh:
                    d = json.load(fh)
                    # not allowed but true with this resource
                    if filename == "aws-cloudformation-customresource.json":
                        d["additionalProperties"] = False
                    errs = list(validator.iter_errors(d))
                    self.assertListEqual(
                        errs, [], f"Error with {dirpath}/{filename}: {errs}"
                    )

    def test_3_cfn_schema_used(self):
        self.assertListEqual(self.used_cfn_schemas, [])
