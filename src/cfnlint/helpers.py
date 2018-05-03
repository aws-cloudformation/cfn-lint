"""
  Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.

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

import fnmatch
import json
import os
import imp
import logging
import re
import requests
import pkg_resources

LOGGER = logging.getLogger(__name__)

TAG_MAP = 'tag:yaml.org,2002:map'
UNCONVERTED_SUFFIXES = ['Ref', 'Condition']
FN_PREFIX = 'Fn::'
CONDITION_FUNCTIONS = ['Fn::If']
REGIONS = ['us-east-1', 'us-east-2', 'us-west-1', 'us-west-2', 'ca-central-1',
           'eu-central-1', 'eu-west-1', 'eu-west-2', 'ap-northeast-1',
           'ap-northeast-2', 'ap-southeast-1', 'ap-southeast-2', 'ap-south-1',
           'sa-east-1']


def load_resources(filename='/data/CloudSpecs/us-east-1.json'):
    """Load resources"""

    filename = pkg_resources.resource_filename(
        __name__,
        filename
    )

    data = json.load(open(filename))

    return data


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


def override_specs(override_spec_data):
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
            if not resource in resources:
                del RESOURCE_SPECS[region]['ResourceTypes'][resource]

def initialize_specs():
    """ Reload Resource Specs """
    for reg in REGIONS:
        RESOURCE_SPECS[reg] = load_resources(filename=('/data/CloudSpecs/%s.json' % reg))


initialize_specs()


def update_resource_specs():
    """ Update Resource Specs """

    # pylint: disable=C0301
    regions = {
        'ap-south-1': 'https://d2senuesg1djtx.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json',
        'ap-northeast-2': 'https://d1ane3fvebulky.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json',
        'ap-southeast-2': 'https://d2stg8d246z9di.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json',
        'ap-southeast-1': 'https://doigdx0kgq9el.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json',
        'ap-northeast-1': 'https://d33vqc0rt9ld30.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json',
        'ca-central-1': 'https://d2s8ygphhesbe7.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json',
        'eu-central-1': 'https://d1mta8qj7i28i2.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json',
        'eu-west-2': 'https://d1742qcu2c1ncx.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json',
        'eu-west-1': 'https://d3teyb21fexa9r.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json',
        'sa-east-1': 'https://d3c9jyj3w509b0.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json',
        'us-east-1': 'https://d1uauaxba7bl26.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json',
        'us-east-2': 'https://dnwj8swjjbsbt.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json',
        'us-west-1': 'https://d68hl49wbnanq.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json',
        'us-west-2': 'https://d201a2mn26r7lk.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json',
    }
    for region, url in regions.items():
        filename = pkg_resources.resource_filename(
            __name__,
            '/data/CloudSpecs/%s.json' % region,
        )
        LOGGER.debug('Downloading template %s into %s', url, filename)
        req = requests.get(url)
        with open(filename, 'wb') as f:
            f.write(req.content)


def load_plugins(directory):
    """Load plugins"""
    result = []
    fh = None

    for root, _, filenames in os.walk(directory):
        for filename in fnmatch.filter(filenames, '[A-Za-z]*.py'):
            pluginname = filename.replace('.py', '')
            try:
                fh, filename, desc = imp.find_module(pluginname, [root])
                mod = imp.load_module(pluginname, fh, filename, desc)
                obj = getattr(mod, pluginname)()
                result.append(obj)
            finally:
                if fh:
                    fh.close()
    return result
