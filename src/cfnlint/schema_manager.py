import filecmp
import fnmatch
import json
import logging
import multiprocessing
import os
import zipfile
from typing import Any, Dict

import jsonpatch

from cfnlint.helpers import (
    REGIONS,
    SPEC_REGIONS,
    apply_json_patch,
    get_url_retrieve,
    load_resource,
    url_has_newer_version,
)

LOGGER = logging.getLogger(__name__)


class ProviderSchemaManager:
    _schemas: Dict[str, Dict[str, dict]] = {}
    _provider_schema_modules: Dict[str, Any] = {}

    def __init__(self) -> None:
        self._schemas: Dict[str, Dict[str, dict]] = {}

        self._patch_path = os.path.join(
            os.path.dirname(__file__),
            "data",
            "ExtendedProviderSchema",
        )
        self._root_path = os.path.join(
            os.path.dirname(__file__),
            "data",
            "ProviderSchemas",
        )

        for region in REGIONS:
            self._schemas[region] = {}

    def get_resource_schema(self, region: str, resource_type: str) -> Dict:
        """Get the provider resource shcema and cache it to speed up future lookups

        Args:
            region (str): the region in which do ge the provider schema for
            resource_type (str): the :: version of the resource type
        Returns:
            dict: returns the schema
        """
        rt = resource_type.replace("::", "-").lower()
        schema = self._schemas[region].get(resource_type)
        if schema is None:
            # dynamically import the modules as needed
            self._provider_schema_modules[region] = __import__(
                f"cfnlint.data.ProviderSchemas.{region}", fromlist=[""]
            )
            # load the schema
            self._schemas[region][resource_type] = load_resource(
                self._provider_schema_modules[region], filename=(f"{rt}.json")
            )
            return self._schemas[region][resource_type]
        return schema

    def update(self, force: bool) -> None:
        self._update_provider_schema("us-east-1", force=force)
        # pylint: disable=not-context-manager
        with multiprocessing.Pool() as pool:
            # Patch from registry schema
            provider_pool_tuple = [
                (k, force) for k, v in SPEC_REGIONS.items() if k != "us-east-1"
            ]
            pool.starmap(self._update_provider_schema, provider_pool_tuple)

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

        directory = os.path.join(f"{self._root_path}/{region}/")

        multiprocessing_logger = multiprocessing.log_to_stderr()

        multiprocessing_logger.debug("Downloading template %s into %s", url, directory)

        # Check to see if we already have the latest version, and if so stop
        if not (url_has_newer_version(url) or force):
            return

        try:
            filehandle = get_url_retrieve(url, caching=True)
            with zipfile.ZipFile(filehandle, "r") as zip_ref:
                zip_ref.extractall(directory)

            for filename in os.listdir(directory):
                with open(f"{directory}{filename}", "r+", encoding="utf-8") as fh:
                    spec = json.load(fh)
                    spec = self._patch_provider_schema(spec, filename, "all")

                    # Back to zero to write spec
                    fh.seek(0)
                    json.dump(spec, fh, indent=1, separators=(",", ": "))
                    # Resize doc as needed
                    fh.truncate()

            # if the region is not us-east-1 compare the files to those in us-east-1
            # symlink if the files are the same
            if region != "us-east-1":
                directory_us_east_1 = os.path.join(f"${self._root_path}/us-east-1/")
                for filename in os.listdir(directory):
                    if filename != "__init__.py":
                        try:
                            if filecmp.cmp(
                                f"{directory}{filename}",
                                f"{directory_us_east_1}{filename}",
                            ):
                                os.remove(f"{directory}{filename}")
                                os.symlink(
                                    f"{directory_us_east_1}{filename}",
                                    f"{directory}{filename}",
                                )
                        except Exception as e:  # pylint: disable=broad-except
                            # Exceptions will typically be the file doesn't exist in us-east-1
                            multiprocessing_logger.debug(
                                "Issuing comparing %s into %s: %s",
                                f"{directory}{filename}",
                                f"{directory_us_east_1}{filename}",
                                e,
                            )

        except Exception:  # pylint: disable=broad-except
            multiprocessing_logger.debug("Issuing updating specs for %s", region)

    def _patch_provider_schema(
        self, content: Dict, source_filename: str, region: str
    ) -> Dict:
        """Patch the resource type schema files"""
        LOGGER.info('Patching provider schema file for region "%s"', region)

        append_dir = os.path.join(self._patch_path, region)
        for dirpath, _, filenames in os.walk(append_dir):
            filenames.sort()
            for filename in fnmatch.filter(filenames, "*.json"):
                if filename == source_filename:
                    file_path = os.path.basename(filename)
                    module = dirpath.replace(f"{append_dir}", f"{region}").replace(
                        os.path.sep, "."
                    )
                    LOGGER.info("Processing patch in %s.%s", module, file_path)
                    all_patches = jsonpatch.JsonPatch(
                        load_resource(
                            f"cfnlint.data.ExtendedProviderSchema.{module}", file_path
                        )
                    )
                    content = apply_json_patch(content, all_patches, region)

        return content

    def update_schemas(self, force: bool):
        pass


PROVIDER_SCHEMA_MANAGER: ProviderSchemaManager = ProviderSchemaManager()
