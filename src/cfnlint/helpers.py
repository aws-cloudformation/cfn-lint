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

import json
import os
import glob
import imp
import logging
import requests
import pkg_resources

LOGGER = logging.getLogger(__name__)

TAG_MAP = "tag:yaml.org,2002:map"
UNCONVERTED_SUFFIXES = ["Ref", "Condition"]
FN_PREFIX = "Fn::"
CONDITION_FUNCTIONS = ['Fn::If']
REGIONS = ['us-east-1', 'us-east-2', 'us-west-1', 'us-west-2', 'ca-central-1',
           'eu-central-1', 'eu-west-1', 'eu-west-2', 'ap-northeast-1',
           'ap-northeast-2', 'ap-southeast-1', 'ap-southeast-2', 'ap-south-1',
           'sa-east-1']

AVAILABILITY_ZONES = [
    'us-east-1a', 'us-east-1b', 'us-east-1c', 'us-east-1d', 'us-east-1e', 'us-east-1f',
    'us-east-2a' 'us-east-2b' 'us-east-2c',
    'us-west-1a', 'us-west-1b', 'us-west-1c',
    'us-west-2a', 'us-west-2b', 'us-west-2c',
    'ca-central-1a', 'ca-central-1b',
    'sa-east-1a', 'sa-east-1b', 'sa-east-1c',
    'eu-west-1a', 'eu-west-1b', 'eu-west-1c',
    'eu-west-2a', 'eu-west-2b', 'eu-west-2c',
    'eu-west-3a', 'eu-west-3b', 'eu-west-3c',
    'eu-central-2a', 'eu-central-2b', 'eu-central-2c',
    'ap-northeast-1a', 'ap-northeast-1b', 'ap-northeast-1c', 'ap-northeast-1d',
    'ap-northeast-2a', 'ap-northeast-2b',
    'ap-northeast-3a',
    'ap-southeast-1a', 'ap-southeast-1b', 'ap-southeast-1c',
    'ap-southeast-2a', 'ap-southeast-2b', 'ap-southeast-2c',
    'ap-south-1a', 'ap-south-1b',
    'cn-north-1a', 'cn-north-1b',
]


def load_resources(filename='/data/CloudSpecs/us-east-1.json'):
    """Load resources"""

    filename = pkg_resources.resource_filename(
        __name__,
        filename
    )

    data = json.load(open(filename))

    return data


RESOURCE_SPECS = {}
for reg in REGIONS:
    RESOURCE_SPECS[reg] = load_resources(filename=("/data/CloudSpecs/%s.json" % reg))


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

    paths = [
        '*/[A-Za-z]*.py',
        '*/*/[A-Za-z]*.py',
    ]
    for path in paths:
        for pluginfile in glob.glob(os.path.join(directory, path)):
            pluginname = os.path.basename(pluginfile.replace('.py', ''))
            dir_name = os.path.dirname(pluginfile)
            try:
                fh, filename, desc = imp.find_module(pluginname, [dir_name])
                mod = imp.load_module(pluginname, fh, filename, desc)
                obj = getattr(mod, pluginname)()
                result.append(obj)
            finally:
                if fh:
                    fh.close()
    return result
