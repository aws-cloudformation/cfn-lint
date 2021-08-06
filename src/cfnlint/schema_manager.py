"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import json
import logging
import os

import botocore.exceptions
import boto3
from cfnlint.helpers import MODULE_SCHEMAS, INVALID_MODULES, MODULES_TO_UPDATE

LOGGER = logging.getLogger(__name__)


class SchemaManager(object):
    """Download schemas if necessary and validate modules"""
    def __init__(
            self, regions):
        self.regions = regions
        self.boto3_sts = boto3.client('sts')
        self.boto3_cfn = boto3.client('cloudformation')

    # Check if the appropriate folder already exists
    def check_folders(self, module_logical_id, name, registry_type):
        account_id = self.boto3_sts.get_caller_identity().get('Account')
        for region in self.regions:
            # windows path can't contain ':'
            path = self.create_path(account_id, region, name.replace(':', '-'))
            if not os.path.isdir(path):
                self.create_folder(path, module_logical_id, name, registry_type, False)
            else:
                self.compare_version_ids(False, path, name, module_logical_id)

    def create_path(self, account_id, region, name):
        return os.path.join(os.path.expanduser('~'), '.cloudformation', account_id, region, name)

    def create_folder(self, path, module_logical_id, name, registry_type, is_update):
        try:
            response = self.aws_call_registry(self.boto3_cfn, module_logical_id, name, registry_type)
            if response:
                MODULE_SCHEMAS.append(path)
                if not is_update:
                    os.makedirs(path)
                self.save_files(response, path)
        except OSError:
            raise OSError

    def aws_call_registry(self, client, module_logical_id, name, registry_type):
        # Recuperate detailed information about a registered extension
        response = None
        try:
            response = client.describe_type(
                Type=registry_type,
                TypeName=name
            )
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'TypeNotFoundException' or e.response['Error']['Code'] \
                    == 'CFNRegistryException':
                if module_logical_id:
                    INVALID_MODULES[module_logical_id] = e.response['Error']['Message']
        return response

    def save_files(self, response, path):
        metadata = {}
        schema = {}

        for field in response:
            if field != 'Schema':
                metadata[field] = response[field]
            else:
                schema[field] = response[field]

        self.create_schema_file(schema, path)
        self.create_metadata_file(metadata, path)

    def create_schema_file(self, data, path):
        try:
            with open(path + '/schema.json', 'w') as f:
                json.dump(data, f, default=str)
        except OSError:
            raise OSError

    def create_metadata_file(self, data, path):
        try:
            with open(path + '/metadata.json', 'w') as f:
                json.dump(data, f, default=str)
        except OSError:
            raise OSError

    def update_locally_cached_schemas(self):
        account_id = self.boto3_sts.get_caller_identity().get('Account')
        folders = []
        for region in self.regions:
            folders.append(os.path.join(os.path.expanduser('~'), '.cloudformation', account_id, region))
        for folder in folders:
            for module in os.listdir(folder):
                self.compare_version_ids(True, os.path.join(folder, module), module)

    def compare_version_ids(self, is_update, path, module, module_logical_id=None):
        if module.endswith('MODULE'):
            local_version_id = self.get_local_version_id(path)
            (registry_version_id, registry_type) = self.get_registry_version_id(self.boto3_cfn,
                                                                                module_logical_id,
                                                                                module.replace('-', ':'))
            MODULE_SCHEMAS.append(path)
            if local_version_id != registry_version_id:
                if is_update:
                    self.create_folder(path, module_logical_id, module.replace('-', ':'), registry_type, is_update)
                else:
                    MODULES_TO_UPDATE.append(module_logical_id)

    def get_local_version_id(self, path):
        with open(path + '/metadata.json') as f:
            return json.loads(f.read())['DefaultVersionId']

    def get_registry_version_id(self, client, module_logical_id, name):
        response = None
        try:
            response = client.list_types(
            )
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'CFNRegistryException':
                INVALID_MODULES[module_logical_id] = e.response['Error']['Message']
        if response:
            for summary in response['TypeSummaries']:
                if summary['TypeName'] == name:
                    return summary['DefaultVersionId'], summary['Type']
        return response
