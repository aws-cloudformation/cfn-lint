"""
  Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.

  Permission is hereby granted, free of charge, to any person obtaining a copy of this
  software and associated documentation files (the "Software"), to deal in the Software
  without restriction, including without limitation the rights to use, copy, modify,
  merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
  permit persons to whom the Software is furnished to do so.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
  INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
  PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
  HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
  OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
  SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import sys
import fnmatch
import json
import os
import imp
import logging
import re
import inspect
import pkg_resources
import six
from cfnlint.decode.node import dict_node, list_node, str_node

LOGGER = logging.getLogger(__name__)

TAG_MAP = 'tag:yaml.org,2002:map'
UNCONVERTED_SUFFIXES = ['Ref', 'Condition']
FN_PREFIX = 'Fn::'
CONDITION_FUNCTIONS = ['Fn::If']
REGIONS = ['us-east-1', 'us-east-2', 'us-west-1', 'us-west-2', 'ca-central-1',
           'eu-central-1', 'eu-west-1', 'eu-west-2', 'ap-northeast-1',
           'ap-northeast-2', 'ap-southeast-1', 'ap-southeast-2', 'ap-south-1',
           'sa-east-1', 'eu-west-3', 'ap-northeast-3', 'us-gov-west-1',
           'us-gov-east-1', 'eu-north-1']

REGEX_ALPHANUMERIC = re.compile('^[a-zA-Z0-9]*$')
REGEX_CIDR = re.compile(r'^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(\/([0-9]|[1-2][0-9]|3[0-2]))$')
REGEX_IPV4 = re.compile(r'^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}$')
REGEX_IPV6 = re.compile(r'^(((?=.*(::))(?!.*\3.+\3))\3?|[\dA-F]{1,4}:)([\dA-F]{1,4}(\3|:\b)|\2){5}(([\dA-F]{1,4}(\3|:\b|$)|\2){2}|(((2[0-4]|1\d|[1-9])?\d|25[0-5])\.?\b){4})\Z', re.I | re.S)
REGEX_DYN_REF = re.compile(r'^.*{{resolve:.+}}.*$')
REGEX_DYN_REF_SSM = re.compile(r'^.*{{resolve:ssm:[a-zA-Z0-9_\.\-/]+:\d+}}.*$')
REGEX_DYN_REF_SSM_SECURE = re.compile(r'^.*{{resolve:ssm-secure:[a-zA-Z0-9_\.\-/]+:\d+}}.*$')


AVAILABILITY_ZONES = [
    'us-east-1a', 'us-east-1b', 'us-east-1c', 'us-east-1d', 'us-east-1e', 'us-east-1f',
    'us-east-2a', 'us-east-2b', 'us-east-2c',
    'us-west-1a', 'us-west-1b', 'us-west-1c',
    'us-west-2a', 'us-west-2b', 'us-west-2c',
    'ca-central-1a', 'ca-central-1b',
    'sa-east-1a', 'sa-east-1b', 'sa-east-1c',
    'eu-west-1a', 'eu-west-1b', 'eu-west-1c',
    'eu-west-2a', 'eu-west-2b', 'eu-west-2c',
    'eu-west-3a', 'eu-west-3b', 'eu-west-3c',
    'eu-central-1a', 'eu-central-1b', 'eu-central-1c',
    'eu-central-2a', 'eu-central-2b', 'eu-central-2c',
    'ap-northeast-1a', 'ap-northeast-1b', 'ap-northeast-1c', 'ap-northeast-1d',
    'ap-northeast-2a', 'ap-northeast-2b',
    'ap-northeast-3a',
    'ap-southeast-1a', 'ap-southeast-1b', 'ap-southeast-1c',
    'ap-southeast-2a', 'ap-southeast-2b', 'ap-southeast-2c',
    'ap-south-1a', 'ap-south-1b',
    'cn-north-1a', 'cn-north-1b',
    'eu-west-3a', 'eu-west-3b', 'eu-west-3c',
    'ap-northeast-3a',
    'us-gov-west-1a', 'us-gov-west-1b', 'us-gov-west-1c',
    'us-gov-east-1a', 'us-gov-east-1b', 'us-gov-east-1c',
    'eu-north-1a', 'eu-north-1b', 'eu-north-1c'
]

FUNCTIONS = [
    'Fn::Base64', 'Fn::GetAtt', 'Fn::GetAZs', 'Fn::ImportValue',
    'Fn::Join', 'Fn::Split', 'Fn::FindInMap', 'Fn::Select', 'Ref',
    'Fn::If', 'Fn::Contains', 'Fn::Sub', 'Fn::Cidr']

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
    }
}


def load_resources(filename='data/CloudSpecs/us-east-1.json'):
    """Load resources"""

    filename = pkg_resources.resource_filename(
        __name__,
        filename
    )

    with open(filename) as fp:
        return json.load(fp)


RESOURCE_SPECS = {}


def merge_spec(source, destination):
    """ Recursive merge spec dict """

    for key, value in source.items():
        if isinstance(value, dict):
            node = destination.setdefault(key, {})
            merge_spec(value, node)
        else:
            destination[key] = value

    return destination


def set_specs(override_spec_data):
    """ Override Resource Specs """

    excludes = []
    includes = []

    # Extract the exclude list from the override file
    if 'ExcludeResourceTypes' in override_spec_data:
        excludes = override_spec_data.pop('ExcludeResourceTypes')
    if 'IncludeResourceTypes' in override_spec_data:
        includes = override_spec_data.pop('IncludeResourceTypes')

    for region, spec in RESOURCE_SPECS.items():

        # Merge override spec file into the AWS Resource specification
        if override_spec_data:
            RESOURCE_SPECS[region] = merge_spec(override_spec_data, spec)

        # Grab a list of all resources
        all_resources = list(RESOURCE_SPECS[region]['ResourceTypes'].keys())[:]

        resources = []

        # Remove unsupported resource using includes
        if includes:
            for include in includes:
                regex = re.compile(include.replace('*', '(.*)') + '$')
                matches = [string for string in all_resources if re.match(regex, string)]

                resources.extend(matches)
        else:
            resources = all_resources[:]

        # Remove unsupported resources using the excludes
        if excludes:
            for exclude in excludes:
                regex = re.compile(exclude.replace('*', '(.*)') + '$')
                matches = [string for string in resources if re.match(regex, string)]

                for match in matches:
                    resources.remove(match)

        # Remove unsupported resources
        for resource in all_resources:
            if resource not in resources:
                del RESOURCE_SPECS[region]['ResourceTypes'][resource]


def is_custom_resource(resource_type):
    """ Return True if resource_type is a custom resource """
    return resource_type and (resource_type == 'AWS::CloudFormation::CustomResource' or resource_type.startswith('Custom::'))


def bool_compare(first, second):
    """ Compare strings to boolean values """

    if isinstance(first, six.string_types):
        first = bool(first.lower() == 'true')

    if isinstance(second, six.string_types):
        second = bool(second.lower() == 'true')

    return first is second


def initialize_specs():
    """ Reload Resource Specs """
    for reg in REGIONS:
        RESOURCE_SPECS[reg] = load_resources(filename=('data/CloudSpecs/%s.json' % reg))


initialize_specs()


def load_plugins(directory):
    """Load plugins"""
    result = []
    fh = None

    def onerror(os_error):
        """Raise an error"""
        raise os_error

    for root, _, filenames in os.walk(directory, onerror=onerror):
        for filename in fnmatch.filter(filenames, '[A-Za-z]*.py'):
            pluginname = filename.replace('.py', '')
            try:
                fh, filename, desc = imp.find_module(pluginname, [root])
                mod = imp.load_module(pluginname, fh, filename, desc)
                for _, clazz in inspect.getmembers(mod, inspect.isclass):
                    method_resolution = inspect.getmro(clazz)
                    if [clz for clz in method_resolution[1:] if clz.__module__ == 'cfnlint' and clz.__name__ == 'CloudFormationLintRule']:
                        # create and instance of subclasses of CloudFormationLintRule
                        obj = clazz()
                        result.append(obj)
            finally:
                if fh:
                    fh.close()

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


def override_specs(override_spec_file):
    """Override specs file"""
    try:
        filename = override_spec_file
        with open(filename) as fp:
            custom_spec_data = json.load(fp)

        set_specs(custom_spec_data)
    except IOError as e:
        if e.errno == 2:
            LOGGER.error('Override spec file not found: %s', filename)
            sys.exit(1)
        elif e.errno == 21:
            LOGGER.error('Override spec file references a directory, not a file: %s', filename)
            sys.exit(1)
        elif e.errno == 13:
            LOGGER.error('Permission denied when accessing override spec file: %s', filename)
            sys.exit(1)
    except (ValueError) as err:
        LOGGER.error('Override spec file %s is malformed: %s', filename, err)
        sys.exit(1)
