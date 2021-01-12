#!/usr/bin/env python
"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import logging
import json
import boto3
from botocore.config import Config
from cfnlint.helpers import get_url_content
from cfnlint.helpers import REGIONS
from cfnlint.maintenance import SPEC_REGIONS

"""
    Updates our dynamic patches from SSM data
    This script requires Boto3 and Credentials to call the SSM API
"""

LOGGER = logging.getLogger('cfnlint')

session = boto3.session.Session()
config = Config(
    retries = {
        'max_attempts': 10,
        'mode': 'standard'
    },
    region_name = 'us-east-1',
)
client = session.client('cloudformation', config=config)


def configure_logging():
    """Setup Logging"""
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    LOGGER.setLevel(logging.INFO)
    log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(log_formatter)

    # make sure all other log handlers are removed before adding it back
    for handler in LOGGER.handlers:
        LOGGER.removeHandler(handler)
    LOGGER.addHandler(ch)

def resolve_refs(properties, schema):
    results = {}
    name = None

    if properties.get('$ref'):
        name = properties.get('$ref').split("/")[-1]
        subname, results = resolve_refs(schema.get('definitions').get(name), schema)
        if subname:
            name = subname
        properties = schema.get('definitions').get(name)

    if properties.get('type') == 'array':
        results = properties.get('items')

    if results:
        properties = results

    if results and results.get('$ref'):
        name, results = resolve_refs(results, schema)

    if not results:
        return name, properties

    return name, results

def get_object_details(name, properties, schema):
    results = {}
    for propname, propdetails in properties.items():
        subname, propdetails = resolve_refs(propdetails, schema)
        t = propdetails.get('type')
        if not t:
            continue
        if t in ['object']:
            if subname is None:
                subname = propname
            if propdetails.get('properties'):
                results.update(get_object_details(name + '.' + subname, propdetails.get('properties'), schema))
            else:
                LOGGER.info("Type %s object for %s has no properties", name, propname)
                continue
        elif t not in ['string', 'integer', 'number', 'boolean']:
            if propdetails.get('$ref'):
                results.update(get_object_details(name + '.' + propname, schema.get('definitions').get(t.get('$ref').split("/")[-1]), schema))
            else:
                LOGGER.info("Unable to handle %s object for %s property", name, propname)
        elif t == 'string':
            if not results.get(name + '.' + propname):
                if propdetails.get('pattern') or (propdetails.get('minLength') and propdetails.get('maxLength')) or propdetails.get('enum'):
                    results[name + '.' + propname] = {}
            if propdetails.get('pattern'):
                results[name + '.' + propname].update({
                    'AllowedPattern': propdetails.get('pattern')
                })
            if propdetails.get('minLength') and propdetails.get('maxLength'):
                results[name + '.' + propname].update({
                    'StringMin': propdetails.get('minLength'),
                    'StringMax': propdetails.get('maxLength'),
                })
            if propdetails.get('enum'):
                results[name + '.' + propname].update({
                    'AllowedValues': propdetails.get('enum')
                })
        elif t in ['number', 'integer']:
            if not results.get(name + '.' + propname):
                if propdetails.get('minimum') and propdetails.get('maximum'):
                    results[name + '.' + propname] = {}
            if propdetails.get('minimum') and propdetails.get('maximum'):
                results[name + '.' + propname].update({
                    'NumberMin': propdetails.get('minimum'),
                    'NumberMax': propdetails.get('maximum'),
                })

    return results

def get_resource_details(name, arn):

    results = {}
    details = client.describe_type(
        Arn=arn,
    )

    schema = json.loads(details.get('Schema'))
    results = get_object_details(name, schema.get('properties'), schema)

    return results

def main():
    """ main function """
    configure_logging()
    results = {}

    nextToken = None
    while True:
        if nextToken:
            types = client.list_types(
                Visibility='PUBLIC',
                Type='RESOURCE',
                DeprecatedStatus='LIVE',
                NextToken=nextToken,
            )
        else:
            types = client.list_types(
                Visibility='PUBLIC',
                Type='RESOURCE',
                DeprecatedStatus='LIVE',
            )

        for t in types.get('TypeSummaries'):
            #if t.get('TypeName') == 'AWS::DataBrew::Recipe':
                if t.get('Description'):
                    results.update(get_resource_details(t.get('TypeName'), t.get('TypeArn')))

        nextToken = types.get('NextToken')
        if not nextToken:
            break

    # Remove duplicates
    vtypes = {}
    for n, v in results.items():
        if n.count('.') > 1:
            s = n.split('.')
            vtypes[s[0] + '.' + '.'.join(s[-2:])] = v
        else:
            vtypes[n] = v

    filevtypes = []
    propvalues = []
    for n, v in vtypes.items():
        element = {
            'op': 'add',
            'path': '/ValueTypes/%s' % (n),
            'value': v,
        }
        filevtypes.append(element)
        if n.count('.') == 2:
            element = {
                'op': 'add',
                'path': '/PropertyTypes/%s/Properties/%s/Value' % (n.split('.')[0], n.split('.')[1]),
                'value': {
                    'ValueType': n,
                },
            }
        else:
            element = {
                'op': 'add',
                'path': '/ResourceTypes/%s/Properties/%s/Value' % (n.split('.')[0], n.split('.')[1]),
                'value': {
                    'ValueType': n,
                },
            }
        propvalues.append(element)

    filename = 'src/cfnlint/data/ExtendedSpecs/all/08_registry_value_types.json'
    with open(filename, 'w+') as f:
        json.dump(filevtypes, f, indent=2, sort_keys=True, separators=(',', ': '))
    filename = 'src/cfnlint/data/ExtendedSpecs/all/09_registry_property_values.json'
    with open(filename, 'w+') as f:
        json.dump(propvalues, f, indent=2, sort_keys=True, separators=(',', ': '))    


if __name__ == '__main__':
    try:
        main()
    except (ValueError, TypeError):
        LOGGER.error(ValueError)
