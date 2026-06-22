"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import json
import logging
import os
import re
import sys
import zipfile
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING, Any, Iterator, Sequence

from cfnlint.helpers import REGIONS, get_url_retrieve, url_has_newer_version
from cfnlint.schema._exceptions import ResourceNotFoundError
from cfnlint.schema._getatts import AttributeDict
from cfnlint.schema._schema import Schema

if TYPE_CHECKING:
    from cfnlint.schema._patch import SchemaPatch

LOGGER = logging.getLogger(__name__)

_ENHANCED_SCHEMAS_URL = (
    "https://github.com/aws-cloudformation/"
    "resource-provider-enhanced-schemas/releases/download/latest/schemas-cfn-lint.zip"
)

_MODULE_SCHEMA = Schema(
    {"additionalProperties": True, "type": "object", "typeName": "Module"}
)


class ProviderSchemaManager:
    def __init__(
        self,
        providers_dir: Path | None = None,
        resources_dir: Path | None = None,
    ) -> None:
        self._providers_dir = providers_dir or Path(
            os.path.dirname(__file__), "..", "data", "schemas", "providers"
        )
        self._resources_dir = resources_dir or Path(
            os.path.dirname(__file__), "..", "data", "schemas", "resources"
        )
        self._registry_schemas: dict[str, Schema] = {}
        self._provider_schema_modules: dict[str, dict[str, str]] = {}
        self._sam_schema_module: dict[str, str] | None = None
        self.reset()

    def reset(self) -> None:
        """
        Reset's the cache so specs can be reloaded.
        Important function when processing many templates
        and using spec patching
        """
        self._schemas: dict[str, dict[str, Schema]] = {}
        for region in REGIONS:
            self._schemas[region] = {}
        self._removed_types: list[str] = []
        self._provider_schema_modules = {}
        self._sam_schema_module = None
        self.get_resource_schema.cache_clear()
        self.get_resource_types.cache_clear()
        self.get_type_getatts.cache_clear()

    def _load_sam_module(self) -> dict[str, str]:
        """Load the SAM provider mapping from sam.json.

        SAM resource types are region-independent and stored in a
        separate pointer file from the per-region provider files.

        Returns:
            Dict mapping SAM resource type to schema hash
        """
        if self._sam_schema_module is None:
            sam_file = self._providers_dir / "sam.json"
            try:
                with open(sam_file, "r", encoding="utf-8") as f:
                    self._sam_schema_module = json.load(f)
            except FileNotFoundError:
                self._sam_schema_module = {}
        return self._sam_schema_module

    def _load_provider_module(self, region: str) -> dict[str, str]:
        """Load the provider mapping for a region from JSON.

        Falls back to us-east-1 if the region file is not available.
        Merges SAM resource types from sam.json.

        Args:
            region: Region name (e.g. 'us-east-1')
        Returns:
            Dict mapping resource type to schema hash
        """
        if region not in self._provider_schema_modules:
            provider_file = self._providers_dir / f"{region}.json"
            if not provider_file.exists():
                provider_file = self._providers_dir / "us-east-1.json"
            try:
                with open(provider_file, "r", encoding="utf-8") as f:
                    self._provider_schema_modules[region] = json.load(f)
            except FileNotFoundError:
                self._provider_schema_modules[region] = {}
            self._provider_schema_modules[region].update(self._load_sam_module())
        return self._provider_schema_modules[region]

    def load_registry_schemas(self, path: str) -> None:
        """Load extra registry schemas from a directory

        Args:
            path (str): the directory to load schema files from
        Returns:
            None: None
        """
        for dirpath, _, filenames in os.walk(path):
            for filename in filenames:
                if not filename.endswith(".json"):
                    continue
                with open(os.path.join(dirpath, filename), "r", encoding="utf-8") as fh:
                    schema = Schema(json.load(fh))
                    self._registry_schemas[schema.type_name] = schema

    def get_resource_schemas_by_regions(
        self, resource_type: str, regions: Sequence[str]
    ) -> Iterator[tuple[list[str], Schema]]:
        """
        Get unique schemas with their associated regions

        Args:
            resource_type (str): the :: version of the resource type
            regions (Sequence[str]): the regions in which we want schems for
        Returns:
            Iterator[tuple[list[str], Schema]]: the unique schemas with
              their associated regions
        """
        resource_type = self._normalize_resource_type(resource_type)

        hash_to_regions: dict[str, list[str]] = {}
        hash_to_schema: dict[str, Schema] = {}

        for region in regions:
            provider_types = self._load_provider_module(region)
            schema_hash = provider_types.get(resource_type)

            if not schema_hash:
                continue

            if schema_hash not in hash_to_regions:
                try:
                    schema = self.get_resource_schema(region, resource_type)
                    hash_to_regions[schema_hash] = []
                    hash_to_schema[schema_hash] = schema
                except ResourceNotFoundError:
                    continue

            hash_to_regions[schema_hash].append(region)

        for schema_hash, region_list in hash_to_regions.items():
            yield region_list, hash_to_schema[schema_hash]

    def _normalize_resource_type(self, resource_type: str) -> str:
        """
        Normalize the resource type to the correct format

        Args:
            resource_type (str): the :: version of the resource type
        Returns:
            str: the normalized resource type
        """
        if resource_type.startswith("Custom::"):
            resource_type = "AWS::CloudFormation::CustomResource"
        if resource_type.endswith("::MODULE"):
            resource_type = "Module"

        return resource_type

    @lru_cache(maxsize=None)
    def get_resource_schema(self, region: str, resource_type: str) -> Schema:
        """Get the provider resource schema and cache it to speed up future lookups

        Args:
            region (str): the region in which do get the provider schema for
            resource_type (str): the :: version of the resource type
        Returns:
            dict: returns the schema
        """
        if resource_type not in self._registry_schemas:
            resource_type = self._normalize_resource_type(resource_type)

        if resource_type in self._removed_types:
            raise ResourceNotFoundError(resource_type, region)

        if resource_type == "Module":
            return _MODULE_SCHEMA

        schema = self._schemas[region].get(resource_type)
        if schema is not None:
            return schema

        if resource_type in self._registry_schemas:
            self._schemas[region][resource_type] = self._registry_schemas[resource_type]
            return self._schemas[region][resource_type]

        provider_types = self._load_provider_module(region)
        schema_hash = provider_types.get(resource_type)

        if not schema_hash:
            raise ResourceNotFoundError(resource_type, region)

        try:
            schema_file = self._resources_dir / f"{schema_hash}.json"
            with open(schema_file, "r", encoding="utf-8") as f:
                self._schemas[region][resource_type] = Schema(json.load(f))
            return self._schemas[region][resource_type]
        except Exception as e:
            raise ResourceNotFoundError(resource_type, region) from e

    @lru_cache(maxsize=None)
    def get_resource_types(self, region: str) -> list[str]:
        """Get the resource types for a region

        Args:
            region (str): the region in which to get the resource types for
        Returns:
            list[str]: returns a list of resource types
        """
        provider_types = self._load_provider_module(region)

        resource_types: list[str] = []
        resource_types.extend(
            rt for rt in provider_types.keys() if rt not in self._removed_types
        )
        resource_types.extend(list(self._registry_schemas.keys()))

        return resource_types

    def update(self, force: bool) -> int:
        """Update schemas from the enhanced schemas repository.

        Args:
            force (bool): force the schemas to be downloaded
        Returns:
            int: exit code (0=success, 2=failure)
        """
        if not (url_has_newer_version(_ENHANCED_SCHEMAS_URL) or force):
            LOGGER.info("Schemas are up to date")
            return 0

        try:
            filehandle = get_url_retrieve(_ENHANCED_SCHEMAS_URL, caching=True)
        except Exception as e:
            LOGGER.error("Failed to download enhanced schemas: %s", e)
            return 2

        with zipfile.ZipFile(filehandle, "r") as zip_ref:
            self._providers_dir.mkdir(parents=True, exist_ok=True)
            self._resources_dir.mkdir(parents=True, exist_ok=True)

            for f in self._providers_dir.glob("*.json"):
                f.unlink()
            for f in self._resources_dir.glob("*.json"):
                f.unlink()

            for name in zip_ref.namelist():
                if not name.endswith(".json"):
                    continue
                if name.startswith("providers/"):
                    dest = self._providers_dir / Path(name).name
                    with zip_ref.open(name) as src, open(dest, "wb") as dst:
                        dst.write(src.read())
                elif name.startswith("resources/"):
                    dest = self._resources_dir / Path(name).name
                    with zip_ref.open(name) as src, open(dest, "wb") as dst:
                        dst.write(src.read())

        LOGGER.info("Schemas updated successfully")
        self.reset()
        return 0

    def patch(self, patch: SchemaPatch, region: str) -> None:
        """Patch the schemas as needed

        Args:
            patch: The patches to be applied to the schemas
        Returns:
            None: Returns when completed
        """

        resource_types = []
        all_resource_types = self.get_resource_types(region)[:]
        # Remove unsupported resource using includes
        if patch.included_resource_types:
            for include in patch.included_resource_types:
                regex = re.compile(include.replace("*", "(.*)") + "$")
                matches = [
                    string for string in all_resource_types if re.match(regex, string)
                ]

                resource_types.extend(matches)
        else:
            resource_types = all_resource_types[:]

        # Remove unsupported resources using the excludes
        for exclude in patch.excluded_resource_types:
            regex = re.compile(exclude.replace("*", "(.*)") + "$")
            matches = [string for string in resource_types if re.match(regex, string)]
            for match in matches:
                resource_types.remove(match)

        # Remove unsupported resources
        removed_types = list(set(all_resource_types) - set(resource_types))
        if removed_types:
            for removed_type in removed_types:
                self._removed_types.append(removed_type)
            self.get_resource_schema.cache_clear()
            self.get_resource_types.cache_clear()

        for resource_type, patches in patch.patches.items():
            try:
                schema = self.get_resource_schema(
                    resource_type=resource_type, region=region
                )
            except ResourceNotFoundError:
                # Resource type doesn't exist in this region
                continue
            try:
                schema.patch(patches=patches)
            except Exception as e:
                print(f"Error applying patch {patches} for {resource_type}: {e}")
                sys.exit(1)

    @lru_cache(maxsize=None)
    def get_type_getatts(self, resource_type: str, region: str) -> AttributeDict:
        """Get the GetAtts for a type in a region

        Args:
            resource_type: The type of the resource. Example: AWS::S3::Bucket
            region: The region to load the resource type from
        Returns:
            Dict(str, Dict): Returns a Dict where the keys are the attributes and the
                value is the CloudFormation schema description of the attribute
        """
        schema = self.get_resource_schema(region=region, resource_type=resource_type)
        return schema.get_atts

    @lru_cache(maxsize=None)
    def get_type_ref(self, resource_type: str, region: str) -> dict[str, Any]:
        """Get the Ref information for a type in a region

        Args:
            resource_type: The type of the resource. Example: AWS::S3::Bucket
            region: The region to load the resource type from
        Returns:
            dict(str, Any): Returns a Dict where the keys are the attributes and the
                value is the CloudFormation schema description of the attribute
        """
        schema = self.get_resource_schema(region=region, resource_type=resource_type)
        return schema.ref


PROVIDER_SCHEMA_MANAGER: ProviderSchemaManager = ProviderSchemaManager()
