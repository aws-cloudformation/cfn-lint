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
import re

TAG_MAP = 'tag:yaml.org,2002:map'
UNCONVERTED_SUFFIXES = ['Ref', 'Condition']
FN_PREFIX = 'Fn::'
CONDITION_FUNCTIONS = ['Fn::If']
REGIONS = ['us-east-1', 'us-east-2', 'us-west-1', 'us-west-2', 'ca-central-1',
           'eu-central-1', 'eu-west-1', 'eu-west-2', 'ap-northeast-1',
           'ap-northeast-2', 'ap-southeast-1', 'ap-southeast-2', 'ap-south-1',
           'sa-east-1']

REGEX_ALPHANUMERIC = re.compile('^[a-zA-Z0-9]*$')
REGEX_CIDR = re.compile(r'^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(\/([0-9]|[1-2][0-9]|3[0-2]))$')
REGEX_IPV4 = re.compile(r'^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}$')
REGEX_IPV6 = re.compile(r'^(((?=.*(::))(?!.*\3.+\3))\3?|[\dA-F]{1,4}:)([\dA-F]{1,4}(\3|:\b)|\2){5}(([\dA-F]{1,4}(\3|:\b|$)|\2){2}|(((2[0-4]|1\d|[1-9])?\d|25[0-5])\.?\b){4})\Z', re.I | re.S)
REGEX_DYN_REF = re.compile(r'^.*{{resolve:.+}}.*$')
REGEX_DYN_REF_SSM = re.compile(r'^.*{{resolve:ssm:[a-zA-Z0-9_\.\-/]+:\d+}}.*$')
REGEX_DYN_REF_SSM_SECURE = re.compile(r'^.*{{resolve:ssm-secure:[a-zA-Z0-9_\.\-/]+:\d+}}.*$')


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
    'eu-central-1a', 'eu-central-1b', 'eu-central-1c',
    'eu-central-2a', 'eu-central-2b', 'eu-central-2c',
    'ap-northeast-1a', 'ap-northeast-1b', 'ap-northeast-1c', 'ap-northeast-1d',
    'ap-northeast-2a', 'ap-northeast-2b',
    'ap-northeast-3a',
    'ap-southeast-1a', 'ap-southeast-1b', 'ap-southeast-1c',
    'ap-southeast-2a', 'ap-southeast-2b', 'ap-southeast-2c',
    'ap-south-1a', 'ap-south-1b',
    'cn-north-1a', 'cn-north-1b',
]

FUNCTIONS = [
    'Fn::Base64', 'Fn::GetAtt', 'Fn::GetAZs', 'Fn::ImportValue',
    'Fn::Join', 'Fn::Split', 'Fn::FindInMap', 'Fn::Select', 'Ref',
    'Fn::If', 'Fn::Contains', 'Fn::Sub', 'Fn::Cidr']

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
