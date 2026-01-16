"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import filecmp
import fnmatch
import json
import logging
import multiprocessing
import os
import re
import shutil
import sys
import zipfile
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Iterator, Sequence

import jsonpatch
import jsonpointer

from cfnlint.helpers import (
    REGION_PRIMARY,
    REGIONS,
    ToPy,
    get_url_retrieve,
    load_resource,
    url_has_newer_version,
)
from cfnlint.schema._exceptions import ResourceNotFoundError
from cfnlint.schema._getatts import AttributeDict
from cfnlint.schema._schema import Schema

if TYPE_CHECKING:
    from cfnlint.schema._patch import SchemaPatch

LOGGER = logging.getLogger(__name__)


class _FileLocation:
    def __init__(self, path: list[str]):
        self.path_relative = os.path.join(
            os.path.dirname(__file__),
            "..",
            *path,
        )
        self.module = ".".join(["cfnlint"] + path[:])
        self.path = path


class ProviderSchemaManager:
    def __init__(self) -> None:
        self._root = _FileLocation(
            [
                "data",
                "schemas",
                "providers",
            ]
        )
        self._patches = _FileLocation(
            [
                "data",
                "schemas",
                "patches",
            ]
        )
        self._region_primary = ToPy(REGION_PRIMARY)
        self._registry_schemas: dict[str, Schema] = {}
        self._provider_schema_modules: dict[str, Any] = {}
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
        self.get_resource_schema.cache_clear()
        self.get_resource_types.cache_clear()
        self.get_type_getatts.cache_clear()

    def load_registry_schemas(self, path: str) -> None:
        """Load extra registry schemas from a directory

        Args:
            path (str): the directory to load schema files from
        Returns:
            None: None
        """
        for dirpath, _, filenames in os.walk(path):
            for filename in fnmatch.filter(filenames, "*.json"):
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
        # Normalize resource type (Custom:: -> AWS::CloudFormation::CustomResource)
        resource_type = self._normalize_resource_type(resource_type)

        # Group regions by schema hash to avoid duplicate validations
        hash_to_regions: dict[str, list[str]] = {}
        hash_to_schema: dict[str, Schema] = {}

        for region in regions:
            # Get the hash for this region's schema first
            reg = ToPy(region)
            if reg.name not in self._provider_schema_modules:
                self._provider_schema_modules[reg.name] = __import__(
                    f"{self._root.module}.{reg.py}", fromlist=[""]
                )
            schema_hash = self._provider_schema_modules[reg.name].types.get(
                resource_type
            )

            if not schema_hash:
                continue

            # Only load schema if we haven't seen this hash before
            if schema_hash not in hash_to_regions:
                try:
                    schema = self.get_resource_schema(region, resource_type)
                    hash_to_regions[schema_hash] = []
                    hash_to_schema[schema_hash] = schema
                except ResourceNotFoundError:
                    continue

            hash_to_regions[schema_hash].append(region)

        # Yield each unique schema with its regions
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

        reg = ToPy(region)
        rt = ToPy(resource_type)

        schema = self._schemas[reg.name].get(rt.name)
        if schema is not None:
            return schema

        # dynamically import the region module as needed
        if reg.name not in self._provider_schema_modules:
            self._provider_schema_modules[reg.name] = __import__(
                f"{self._root.module}.{reg.py}", fromlist=[""]
            )

        # check cfn-lint provided schemas
        if rt.name in self._registry_schemas:
            self._schemas[reg.name][rt.name] = self._registry_schemas[rt.name]
            return self._schemas[reg.name][rt.name]

        # load the schema from hash-based storage
        region_module = self._provider_schema_modules[reg.name]
        schema_hash = region_module.types.get(resource_type)

        if not schema_hash:
            raise ResourceNotFoundError(rt.name, region)

        try:
            # Load from resources directory using hash
            resources_module = __import__(
                "cfnlint.data.schemas.resources", fromlist=[""]
            )
            self._schemas[reg.name][rt.name] = Schema(
                load_resource(
                    resources_module,
                    filename=f"{schema_hash}.json",
                )
            )
            return self._schemas[reg.name][rt.name]
        except Exception as e:
            raise ResourceNotFoundError(rt.name, region) from e

    @lru_cache(maxsize=None)
    def get_resource_types(self, region: str) -> list[str]:
        """Get the resource types for a region

        Args:
            region (str): the region in which to get the resource types for
        Returns:
            list[str]: returns a list of resource types
        """
        reg = ToPy(region)

        if reg.name not in self._provider_schema_modules:
            self._provider_schema_modules[reg.name] = __import__(
                f"{self._root.module}.{reg.py}", fromlist=[""]
            )

        resource_types: list[str] = []
        resource_types.extend(
            rt
            for rt in self._provider_schema_modules[reg.name].types.keys()
            if rt not in self._removed_types
        )
        resource_types.extend(list(self._registry_schemas.keys()))

        return resource_types

    def update(self, force: bool) -> int:
        """Update every regions provider schemas

        Args:
            force (bool): force the schemas to be downloaded
        Returns:
            int: exit code (0=success, 1=partial failure, 2=complete failure)
        """
        import hashlib
        from pathlib import Path

        # Separate ISO regions (not publicly accessible) from regular regions
        iso_regions = [r for r in REGIONS if "iso" in r or r.startswith("eusc")]
        regular_regions = [r for r in REGIONS if r not in iso_regions]

        # Download all regular regions in parallel
        downloaded_regions: dict[str, dict[str, dict]] = {}
        failed_regions: list[str] = []

        # pylint: disable=not-context-manager
        with multiprocessing.Pool() as pool:
            results = pool.starmap(
                self._download_region_schemas,
                [(region, force) for region in regular_regions],
            )

        for region, result in zip(regular_regions, results):
            if result is None:
                # Actual failure
                failed_regions.append(region)
            elif result is False:
                # No update needed, skip
                pass
            elif isinstance(result, dict):
                # Successfully downloaded
                downloaded_regions[region] = result

        if not downloaded_regions:
            # No regions were updated
            if failed_regions:
                # All regular regions failed
                LOGGER.error("All regions failed to download")
                return 2
            else:
                # All regions are up to date
                LOGGER.info("All schemas are up to date")
                return 0

        # Build global hash map
        hash_to_schema = {}
        region_mappings: dict[str, dict[str, str]] = {}

        for region, schemas in downloaded_regions.items():
            region_mappings[region] = {}
            for resource_type, schema_content in schemas.items():
                schema_hash = hashlib.sha256(
                    json.dumps(schema_content, sort_keys=True).encode()
                ).hexdigest()[:16]

                hash_to_schema[schema_hash] = schema_content
                region_mappings[region][resource_type] = schema_hash

        # Write unique schemas
        resources_dir = Path(self._root.path_relative).parent / "resources"
        resources_dir.mkdir(exist_ok=True)

        for schema_hash, schema_content in hash_to_schema.items():
            with open(
                resources_dir / f"{schema_hash}.json", "w", encoding="utf-8"
            ) as f:
                json.dump(
                    schema_content, f, indent=1, separators=(",", ": "), sort_keys=True
                )
                f.write("\n")

        # Write region mapping files
        for region, type_map in region_mappings.items():
            self._write_region_file(region, type_map)

        # Handle ISO regions by copying us-east-1 schemas
        if "us-east-1" in region_mappings:
            for region in iso_regions:
                self._write_region_file(region, region_mappings["us-east-1"])

        # Cleanup orphaned schemas
        self._cleanup_orphaned_schemas(region_mappings, resources_dir)

        if failed_regions:
            LOGGER.warning(
                f"Failed regions (kept existing): {', '.join(failed_regions)}"
            )
            return 1

        return 0

    def _download_region_schemas(
        self, region: str, force: bool = False
    ) -> dict[str, dict] | None | bool:
        """Download schemas for a single region

        Args:
            region: Region to download
            force: Force download even if cached
        Returns:
            Dict mapping resource type to schema content,
                False if no update needed, or None on failure
        """

        suffix = ".cn" if region in ["cn-north-1", "cn-northwest-1"] else ""
        url = f"https://schema.cloudformation.{region}.amazonaws.com{suffix}/CloudformationSchema.zip"

        multiprocessing_logger = multiprocessing.log_to_stderr()
        multiprocessing_logger.debug(f"Downloading {url}")

        # Check if update needed
        if not (url_has_newer_version(url) or force):
            return False

        try:
            filehandle = get_url_retrieve(url, caching=True)
            schemas = {}

            with zipfile.ZipFile(filehandle, "r") as zip_ref:
                for filename in zip_ref.namelist():
                    if filename.endswith(".json"):
                        with zip_ref.open(filename) as f:
                            spec = json.load(f)
                            # Apply patches and cleanup
                            if "handlers" in spec:
                                del spec["handlers"]
                            if "tagging" in spec and "permissions" in spec.get(
                                "tagging", {}
                            ):
                                del spec["tagging"]["permissions"]
                            spec = self._remove_descriptions(spec)
                            spec = self._patch_provider_schema(spec, filename, "all")
                            spec = self._patch_provider_schema(
                                spec, filename, region=ToPy(region).py
                            )

                            schemas[spec["typeName"]] = spec

            # Add synthetic types
            schemas["AWS::CDK::Metadata"] = {"typeName": "AWS::CDK::Metadata"}
            schemas["Module"] = {
                "additionalProperties": True,
                "type": "object",
                "typeName": "Module",
            }

            return schemas

        except Exception as e:
            LOGGER.warning(f"Failed downloading {region}: {e}")
            return None

    def _write_region_file(self, region: str, type_map: dict[str, str]) -> None:
        """Write region .py file with type to hash mapping

        Args:
            region: Region name
            type_map: Dict mapping resource type to schema hash
        """
        from pathlib import Path

        reg = ToPy(region)
        region_file = Path(self._root.path_relative) / f"{reg.py}.py"

        with open(region_file, "w", encoding="utf-8") as f:
            f.write("# ruff: noqa: E501, PLR0915\n")
            f.write("from __future__ import annotations\n\n")
            f.write("types: dict[str, str] = {\n")
            for resource_type in sorted(type_map.keys()):
                schema_hash = type_map[resource_type]
                f.write(f'    "{resource_type}": "{schema_hash}",\n')
            f.write("}\n")

    def _cleanup_orphaned_schemas(self, region_mappings: dict, resources_dir) -> None:
        """Remove schema files no longer referenced by any region

        Args:
            region_mappings: Dict of region to type mappings (newly downloaded)
            resources_dir: Path to resources directory
        """
        from pathlib import Path

        # Collect all referenced hashes from newly downloaded regions
        referenced_hashes = set()
        for type_map in region_mappings.values():
            referenced_hashes.update(type_map.values())

        # Also check existing provider files for regions that weren't updated
        providers_dir = Path(self._root.path_relative)
        for provider_file in providers_dir.glob("*.py"):
            if provider_file.name == "__init__.py":
                continue
            try:
                # Import the provider module to get its types dict
                region_name = provider_file.stem
                module_name = f"cfnlint.data.schemas.providers.{region_name}"
                provider = __import__(module_name, fromlist=["types"])
                if hasattr(provider, "types"):
                    referenced_hashes.update(provider.types.values())
            except (ImportError, AttributeError):
                continue

        # Remove unreferenced files
        for schema_file in Path(resources_dir).glob("*.json"):
            schema_hash = schema_file.stem
            if schema_hash not in referenced_hashes:
                LOGGER.info(f"Removing orphaned schema: {schema_hash}")
                schema_file.unlink()

    def _remove_descriptions(self, spec: Any) -> Any:
        if isinstance(spec, dict):
            r: dict[Any, Any] = {}
            for k, v in spec.items():
                if k != "description":
                    r[k] = self._remove_descriptions(v)

            return r
        elif isinstance(spec, list):
            m: list[Any] = []
            for v in spec:
                m.append(self._remove_descriptions(v))

            return m
        else:
            return spec

    def _update_provider_schema(self, region: str, force: bool = False) -> None:
        """Update the provider schemas from the AWS websites

        Args:
            region (str): the region in which do ge the provider schema for
            force (bool): force the schemas to be downloaded
        Returns:
            None: returns when complete
        """
        # China regions in .com.cn
        suffix = ".cn" if region in ["cn-north-1", "cn-northwest-1"] else ""
        url = f"https://schema.cloudformation.{region}.amazonaws.com{suffix}/CloudformationSchema.zip"
        reg = ToPy(region)
        directory = os.path.join(f"{self._root.path_relative}/{reg.py}/")
        directory_pr = os.path.join(
            f"{self._root.path_relative}/{self._region_primary.py}/"
        )

        multiprocessing_logger = multiprocessing.log_to_stderr()

        multiprocessing_logger.debug("Downloading template %s into %s", url, directory)

        if "iso" in region or region.startswith("eusc"):
            all_types = ["AWS::CDK::Metadata", "Module"]
            cached = ["Module"]
            filenames = [
                f
                for f in os.listdir(directory_pr)
                if os.path.isfile(os.path.join(directory_pr, f)) and f != "__init__.py"
            ]
            for filename in filenames:
                with open(f"{directory_pr}{filename}", "r+", encoding="utf-8") as fh:
                    spec = json.load(fh)
                    all_types.append(spec["typeName"])
                cached.append(filename)

            with open(f"{directory}__init__.py", encoding="utf-8", mode="w") as f:
                f.write("from __future__ import annotations\n\n")
                f.write("# pylint: disable=too-many-lines\ntypes: list[str] = [\n")
                for rt in sorted(all_types):
                    f.write(f'    "{rt}",\n')
                f.write(
                    "]\n\n# pylint: disable=too-many-lines\ncached: list[str] = [\n"
                )
                for cache_file in sorted(cached):
                    f.write(f'    "{cache_file}",\n')
                f.write("]\n")

        # Check to see if we already have the latest version, and if so stop
        if not (url_has_newer_version(url) or force):
            return

        if not os.path.exists(directory):
            os.mkdir(directory)

        try:
            filehandle = get_url_retrieve(url, caching=True)
            # clean folder
            shutil.rmtree(directory)
            with zipfile.ZipFile(filehandle, "r") as zip_ref:
                zip_ref.extractall(directory)

            filenames = [
                f
                for f in os.listdir(directory)
                if os.path.isfile(os.path.join(directory, f)) and f != "__init__.py"
            ]
            # There is no schema for CDK but its an allowable type
            all_types = ["AWS::CDK::Metadata", "Module"]
            for filename in filenames:
                with open(f"{directory}{filename}", "r+", encoding="utf-8") as fh:
                    spec = json.load(fh)
                    all_types.append(spec["typeName"])

                    # Apply patches to the schema
                    spec = self._patch_provider_schema(spec, filename, "all")
                    spec = self._patch_provider_schema(
                        spec, filename, region=ToPy(region).py
                    )

                    # Write the patched schema back
                    fh.seek(0)
                    json.dump(
                        spec, fh, indent=1, separators=(",", ": "), sort_keys=True
                    )
                    fh.write("\n")
                    fh.truncate()

            # if the region is not us-east-1 compare the files to those in us-east-1
            # symlink if the files are the same
            if reg.name != self._region_primary.name:
                cached = ["Module"]
                for filename in os.listdir(directory):
                    if filename != "__init__.py":
                        try:
                            if filecmp.cmp(
                                f"{directory}{filename}",
                                f"{directory_pr}{filename}",
                            ):
                                cached.append(filename)
                                os.remove(f"{directory}{filename}")
                        except FileNotFoundError:
                            pass
                        except Exception as e:  # pylint: disable=broad-except
                            # Exceptions will typically be the file
                            # doesn't exist in primary region
                            LOGGER.info(
                                "Issuing comparing %s into %s: %s",
                                f"{directory}{filename}",
                                f"{directory_pr}{filename}",
                                e,
                            )
                with open(f"{directory}__init__.py", encoding="utf-8", mode="w") as f:
                    f.write("from __future__ import annotations\n\n")
                    f.write("# pylint: disable=too-many-lines\ntypes: list[str] = [\n")
                    for rt in sorted(all_types):
                        f.write(f'    "{rt}",\n')
                    f.write(
                        "]\n\n# pylint: disable=too-many-lines\ncached: list[str] = [\n"
                    )
                    for cache_file in sorted(cached):
                        f.write(f'    "{cache_file}",\n')
                    f.write("]\n")
            else:
                with open(f"{directory}__init__.py", encoding="utf-8", mode="w") as f:
                    f.write("from __future__ import annotations\n\n")
                    f.write("# pylint: disable=too-many-lines\ntypes: list[str] = [\n")
                    for rt in sorted(all_types):
                        f.write(f'    "{rt}",\n')
                    f.write("]\ncached: list[str] = []\n")

        except Exception as e:  # pylint: disable=broad-except
            LOGGER.info("Issuing updating schemas for %s: %s", region, e)

    def patch_schemas(self) -> None:
        """Patch schemas in the hash-based storage system"""
        resources_dir = Path(self._root.path_relative).parent / "resources"
        if not resources_dir.exists():
            LOGGER.info("Resources directory not found, skipping patching")
            return

        # Get all schema files
        schema_files = list(resources_dir.glob("*.json"))
        LOGGER.info("Patching %d schema files", len(schema_files))

        patched_count = 0
        for schema_file in schema_files:
            try:
                # Load the schema
                with open(schema_file, "r", encoding="utf-8") as f:
                    spec = json.load(f)

                original_spec = json.dumps(spec, sort_keys=True)

                # Apply standard patches
                if "handlers" in spec:
                    del spec["handlers"]
                if "tagging" in spec and "permissions" in spec.get("tagging", {}):
                    del spec["tagging"]["permissions"]

                spec = self._remove_descriptions(spec)

                # Apply provider-specific patches based on typeName
                if "typeName" in spec:
                    type_name = spec["typeName"]
                    filename = f"{type_name.lower().replace('::', '_')}.json"
                    spec = self._patch_provider_schema(spec, filename, "all")

                # Check if the schema was modified
                modified_spec = json.dumps(spec, sort_keys=True)
                if original_spec != modified_spec:
                    # Write the patched schema back to the same file
                    with open(schema_file, "w", encoding="utf-8") as f:
                        json.dump(
                            spec, f, indent=1, separators=(",", ": "), sort_keys=True
                        )
                        f.write("\n")
                    patched_count += 1
                    LOGGER.debug("Patched schema: %s", schema_file.name)

            except Exception as e:
                LOGGER.info("Error patching %s: %s", schema_file.name, e)

        LOGGER.info(
            "Patched %d out of %d schema files", patched_count, len(schema_files)
        )

    def _patch_provider_schema(
        self, content: Dict, source_filename: str, region: str
    ) -> Dict:
        """Provides the logic to patch a CloudFormation provider schema file.

        Args:
            content: A Dict representing the data that needs to be patched
            source_filename: The source filename for the JSON patches
            region: The region to apply the patch against
        Returns:
            Dict: returns the patched content
        """
        for patch_type in ["providers", "extensions"]:
            source_dir = source_filename.replace("-", "_").replace(".json", "")
            append_dir = os.path.join(
                self._patches.path_relative, patch_type, region, source_dir
            )
            for dirpath, _, filenames in os.walk(append_dir):
                filenames.sort()
                for filename in fnmatch.filter(filenames, "*.json"):
                    file_path = os.path.basename(filename)
                    module = dirpath.replace(f"{append_dir}", f"{region}").replace(
                        os.path.sep, "."
                    )
                    try:
                        jsonpatch.JsonPatch(
                            load_resource(
                                f"{self._patches.module}.{patch_type}.{module}.{source_dir}",
                                file_path,
                            )
                        ).apply(content, in_place=True)
                    except jsonpatch.JsonPatchConflict as e:
                        LOGGER.info(
                            "Patch already applied %s: %s",
                            os.path.join(append_dir, file_path),
                            str(e),
                        )
                    except jsonpatch.JsonPatchTestFailed as e:
                        LOGGER.info(
                            "Patch test failed %s: %s",
                            os.path.join(append_dir, file_path),
                            str(e),
                        )
                    except jsonpatch.JsonPatchException as e:
                        LOGGER.info(
                            "Patch exception raised for %s: %s",
                            os.path.join(append_dir, file_path),
                            str(e),
                        )
                    except jsonpointer.JsonPointerException as e:
                        LOGGER.info(
                            "Patch exception with pointer %s: %s",
                            os.path.join(append_dir, file_path),
                            str(e),
                        )
                    except Exception as e:  # pylint: disable=broad-exception-caught
                        LOGGER.info(
                            "Unknown exception raised applying patch %s: %s",
                            os.path.join(append_dir, file_path),
                            str(e),
                        )

        return content

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
        resource_type = self._normalize_resource_type(resource_type)
        self.get_resource_schema(region=region, resource_type=resource_type)
        return self._schemas[region][resource_type].get_atts

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
        resource_type = self._normalize_resource_type(resource_type)
        self.get_resource_schema(region=region, resource_type=resource_type)
        return self._schemas[region][resource_type].ref


PROVIDER_SCHEMA_MANAGER: ProviderSchemaManager = ProviderSchemaManager()
