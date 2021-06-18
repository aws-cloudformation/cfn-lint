"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import json
import logging
import os
import platform

import botocore.exceptions
import boto3
from cfnlint.template import Template

LOGGER = logging.getLogger(__name__)


class SchemaManager(object):
    """Download schemas if necessary and validate modules"""
    def __init__(
            self, filename, template, regions):
        self.filename = filename
        self.regions = regions
        self.template = Template(filename, template, regions)
        self.boto3_sts = boto3.client('sts')
        self.boto3_cfn = boto3.client('cloudformation')

    # Check if the appropriate folder already exists
    def check_folders(self, name, registry_type):
        account_id = self.boto3_sts.get_caller_identity().get('Account')
        username = None
        path_split = os.getcwd().split('/')
        try:
            index = path_split.index('Users')
            username = path_split[index + 1]
        except ValueError:
            raise ValueError

        is_windows = platform.system() == 'win32'

        for region in self.regions:
            path = self.create_path(is_windows, username, account_id, region, name)

            if not os.path.isdir(path):
                self.create_folder(path, name, registry_type)

    def create_path(self, is_windows, username, account_id, region, name):
        if is_windows:
            path = os.path.join(r'C:\Users', username, 'AppData', 'cloudformation', account_id, region, name)
        else:
            path = os.path.join('/Users', username, '.cloudformation', account_id, region, name)
        return path

    def create_folder(self, path, name, registry_type):
        try:
            response = self.aws_call_registry(self.boto3_cfn, name, registry_type)
            if response:
                os.makedirs(path)
                self.save_files(response, path)
        except OSError:
            raise OSError

    def aws_call_registry(self, client, name, registry_type):
        # Recuperate detailed information about a registered extension
        response = None
        try:
            response = client.describe_type(
                Type=registry_type,
                TypeName=name
            )
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'TypeNotFoundException':
                print(e.response['Error']['Message'])
            if e.response['Error']['Code'] == 'CFNRegistryException':
                print(e.response['Error']['Message'])
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
