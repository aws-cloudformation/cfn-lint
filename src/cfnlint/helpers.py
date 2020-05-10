"""
Helpers for loading resources, managing specs, constants, etc.

Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import sys
import fnmatch
import json
import os
import datetime
import logging
import re
import inspect
import six
from cfnlint.decode.node import dict_node, list_node, str_node


if sys.version_info < (3,):
    import imp
else:
    import importlib  # pylint: disable=ungrouped-imports

LOGGER = logging.getLogger(__name__)

TAG_MAP = 'tag:yaml.org,2002:map'
UNCONVERTED_SUFFIXES = ['Ref', 'Condition']
FN_PREFIX = 'Fn::'
CONDITION_FUNCTIONS = ['Fn::If']

REGEX_ALPHANUMERIC = re.compile('^[a-zA-Z0-9]*$')
REGEX_CIDR = re.compile(
    r'^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(\/([0-9]|[1-2][0-9]|3[0-2]))$')
REGEX_IPV4 = re.compile(
    r'^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}$')
REGEX_IPV6 = re.compile(
    r'^(((?=.*(::))(?!.*\3.+\3))\3?|[\dA-F]{1,4}:)([\dA-F]{1,4}(\3|:\b)|\2){5}(([\dA-F]{1,4}(\3|:\b|$)|\2){2}|(((2[0-4]|1\d|[1-9])?\d|25[0-5])\.?\b){4})\Z', re.I | re.S)
REGEX_DYN_REF = re.compile(r'^.*{{resolve:.+}}.*$')
REGEX_DYN_REF_SSM = re.compile(r'^.*{{resolve:ssm:[a-zA-Z0-9_\.\-/]+:\d+}}.*$')
REGEX_DYN_REF_SSM_SECURE = re.compile(r'^.*{{resolve:ssm-secure:[a-zA-Z0-9_\.\-/]+:\d+}}.*$')


AVAILABILITY_ZONES = [
    'af-south-1a', 'af-south-1b', 'af-south-1c',
    'ap-east-1a', 'ap-east-1b', 'ap-east-1c',
    'ap-northeast-1a', 'ap-northeast-1b', 'ap-northeast-1c', 'ap-northeast-1d',
    'ap-northeast-2a', 'ap-northeast-2b', 'ap-northeast-2c',
    'ap-northeast-3a',
    'ap-south-1a', 'ap-south-1b', 'ap-south-1c',
    'ap-southeast-1a', 'ap-southeast-1b', 'ap-southeast-1c',
    'ap-southeast-2a', 'ap-southeast-2b', 'ap-southeast-2c',
    'ca-central-1a', 'ca-central-1b', 'ca-central-1d',
    'cn-north-1a', 'cn-north-1b',
    'cn-northwest-1a', 'cn-northwest-1b', 'cn-northwest-1c',
    'eu-central-1a', 'eu-central-1b', 'eu-central-1c',
    'eu-north-1a', 'eu-north-1b', 'eu-north-1c',
    'eu-south-1a', 'eu-south-1b', 'eu-south-1c',
    'eu-west-1a', 'eu-west-1b', 'eu-west-1c',
    'eu-west-2a', 'eu-west-2b', 'eu-west-2c',
    'eu-west-3a', 'eu-west-3b', 'eu-west-3c',
    'me-south-1a', 'me-south-1b', 'me-south-1c',
    'sa-east-1a', 'sa-east-1b', 'sa-east-1c',
    'us-east-1a', 'us-east-1b', 'us-east-1c', 'us-east-1d', 'us-east-1e', 'us-east-1f',
    'us-east-2a', 'us-east-2b', 'us-east-2c',
    'us-gov-east-1a', 'us-gov-east-1b', 'us-gov-east-1c',
    'us-gov-west-1a', 'us-gov-west-1b', 'us-gov-west-1c',
    'us-west-1a', 'us-west-1b', 'us-west-1c',
    'us-west-2a', 'us-west-2b', 'us-west-2c', 'us-west-2d', 'us-west-2-lax-1a',
]

FUNCTIONS = [
    'Fn::Base64', 'Fn::GetAtt', 'Fn::GetAZs', 'Fn::ImportValue',
    'Fn::Join', 'Fn::Split', 'Fn::FindInMap', 'Fn::Select', 'Ref',
    'Fn::If', 'Fn::Contains', 'Fn::Sub', 'Fn::Cidr']

FUNCTIONS_MULTIPLE = ['Fn::GetAZs', 'Fn::Split']

# FindInMap can be singular or multiple.  This needs to be accounted for individually
FUNCTIONS_SINGLE = list(set(FUNCTIONS) - set(FUNCTIONS_MULTIPLE) - set('Fn::FindInMap'))

FUNCTION_IF = 'Fn::If'
FUNCTION_AND = 'Fn::And'
FUNCTION_OR = 'Fn::Or'
FUNCTION_NOT = 'Fn::Not'
FUNCTION_EQUALS = 'Fn::Equals'

PSEUDOPARAMS = [
    'AWS::AccountId',
    'AWS::NotificationARNs',
    'AWS::NoValue',
    'AWS::Partition',
    'AWS::Region',
    'AWS::StackId',
    'AWS::StackName',
    'AWS::URLSuffix'
]

LIMITS = {
    'mappings': {
        'number': 100,
        'attributes': 64,
        'name': 255  # in characters
    },
    'outputs': {
        'number': 60,
        'name': 255,  # in characters
        'description': 1024  # in bytes
    },
    'parameters': {
        'number': 60,
        'name': 255,  # in characters
        'value': 4096  # in bytes
    },
    'resources': {
        'number': 200,
        'name': 255  # in characters
    },
    'template': {
        'body': 460800,  # in bytes
        'description': 1024  # in bytes
    },
    'threshold': 0.9,  # for rules about approaching the other limit values
}

valid_snapshot_types = [
    'AWS::EC2::Volume',
    'AWS::ElastiCache::CacheCluster',
    'AWS::ElastiCache::ReplicationGroup',
    'AWS::Neptune::DBCluster',
    'AWS::RDS::DBCluster',
    'AWS::RDS::DBInstance',
    'AWS::Redshift::Cluster'
]


def is_custom_resource(resource_type):
    """ Return True if resource_type is a custom resource """
    return resource_type and (resource_type == 'AWS::CloudFormation::CustomResource' or resource_type.startswith('Custom::'))


def bool_compare(first, second):
    """ Compare strings to boolean values """

    if isinstance(first, six.string_types):
        first = bool(first.lower() in ['true', 'True'])

    if isinstance(second, six.string_types):
        second = bool(second.lower() in ['true', 'True'])

    return first is second


def format_json_string(json_string):
    """ Format the given JSON string"""
    def converter(o):  # pylint: disable=R1710
        """ Help convert date/time into strings """
        if isinstance(o, datetime.datetime):
            return o.__str__()
    return json.dumps(json_string, indent=2, sort_keys=True, separators=(',', ': '), default=converter)


def create_rules(mod):
    """Create and return an instance of each CloudFormationLintRule subclass
    from the given module."""
    result = []
    for _, clazz in inspect.getmembers(mod, inspect.isclass):
        method_resolution = inspect.getmro(clazz)
        if [clz for clz in method_resolution[1:] if clz.__module__ in ('cfnlint', 'cfnlint.rules') and clz.__name__ == 'CloudFormationLintRule']:
            # create and instance of subclasses of CloudFormationLintRule
            obj = clazz()
            result.append(obj)
    return result


if sys.version_info < (3,):
    def import_filename(pluginname, root):
        """ import_filename imports a module from a file"""
        fh = None
        try:
            fh, filename, desc = imp.find_module(pluginname, [root])
            mod = imp.load_module(pluginname, fh, filename, desc)
            return mod
        finally:
            if fh:
                fh.close()

        return None

else:
    loader_details = (
        importlib.machinery.SourceFileLoader,  # pylint: disable=no-member
        importlib.machinery.SOURCE_SUFFIXES  # pylint: disable=no-member
    )

    def import_filename(pluginname, root):
        """ import_filename imports a module from a file"""
        mod_finder = importlib.machinery.FileFinder(  # pylint: disable=no-member
            root, loader_details)

        mod_spec = mod_finder.find_spec(pluginname)
        if mod_spec is not None:
            if sys.version_info < (3, 5):
                # for python 2.7 disabling pylint checks
                mod = mod_spec.loader.load_module()  # pylint: disable=no-member
                return mod
            # for python 2.7 disabling pylint checks
            mod = importlib.util.module_from_spec(mod_spec)  # pylint: disable=no-member
            mod_spec.loader.exec_module(mod)
            return mod

        return None


def load_plugins(directory):
    """Load plugins"""
    result = []

    def onerror(os_error):
        """Raise an error"""
        raise os_error

    for root, _, filenames in os.walk(directory, onerror=onerror):
        for filename in fnmatch.filter(filenames, '[A-Za-z]*.py'):
            mod = import_filename(filename.replace('.py', ''), root)
            if mod is not None:
                result.extend(create_rules(mod))

    return result


def convert_dict(template, start_mark=(0, 0), end_mark=(0, 0)):
    """Convert dict to template"""
    if isinstance(template, dict):
        if not isinstance(template, dict_node):
            template = dict_node(template, start_mark, end_mark)
        for k, v in template.copy().items():
            k_start_mark = start_mark
            k_end_mark = end_mark
            if isinstance(k, str_node):
                k_start_mark = k.start_mark
                k_end_mark = k.end_mark
            new_k = str_node(k, k_start_mark, k_end_mark)
            del template[k]
            template[new_k] = convert_dict(v, k_start_mark, k_end_mark)
    elif isinstance(template, list):
        if not isinstance(template, list_node):
            template = list_node(template, start_mark, end_mark)
        for i, v in enumerate(template):
            template[i] = convert_dict(v, start_mark, end_mark)

    return template
