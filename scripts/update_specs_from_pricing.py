#!/usr/bin/env python
"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

"""
    Updates our dynamic patches from the pricing API
    This script requires Boto3 and Credentials to call the Pricing API
"""

import boto3
import json
import logging


LOGGER = logging.getLogger('cfnlint')


region_map = {
    'US East (N. Virginia)': 'us-east-1',
    'Asia Pacific (Mumbai)': 'ap-south-1',
    'US East (Ohio)': 'us-east-2',
    'US West (Oregon)': 'us-west-2',
    'AWS GovCloud (US-East)': 'us-gov-east-1',
    'Asia Pacific (Hong Kong)': 'ap-east-1',
    'Asia Pacific (Tokyo)': 'ap-northeast-1',
    'EU (Stockholm)': 'eu-north-1',
    'Asia Pacific (Singapore)': 'ap-southeast-1',
    'Asia Pacific (Osaka-Local)': 'ap-northeast-3',
    'EU (London)': 'eu-west-2',
    'South America (Sao Paulo)': 'sa-east-1',
    'Asia Pacific (Sydney)': 'ap-southeast-2',
    'EU (Ireland)': 'eu-west-1',
    'EU (Frankfurt)': 'eu-central-1',
    'EU (Paris)': 'eu-west-3',
    'Canada (Central)': 'ca-central-1',
    'Asia Pacific (Seoul)': 'ap-northeast-2',
    'AWS GovCloud (US)': 'us-gov-west-1',
    'US West (N. California)': 'us-west-1',
    'China (Beijing)': 'cn-north-1',
    'China (Ningxia)': 'cn-northwest-1',
    'Middle East (Bahrain)': 'me-south-1',
}

session = boto3.session.Session()
client = session.client('pricing', region_name='us-east-1')

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


def update_outputs(key, values, outputs):
    """ update outputs with appropriate results """
    for region in values:
        element = {
            "op": "add",
            "path": "/ValueTypes/%s/AllowedValues" % key,
            "value": sorted(values[region])
        }
        outputs[region].append(element)

    return outputs


def get_ec2_pricing():
    """ Get Ec2 Pricing """

    LOGGER.info('Get EC2 pricing')
    paginator = client.get_paginator('get_products')
    page_iterator = paginator.paginate(
        ServiceCode='AmazonEC2',
        FormatVersion='aws_v1',
    )

    results = {}
    for page in page_iterator:
        for price_item in page.get('PriceList', []):
            products = json.loads(price_item)
            product = products.get('product', {})
            if product:
                if product.get('productFamily') in ['Compute Instance', 'Compute Instance (bare metal)']:
                    if not results.get(region_map[product.get('attributes').get('location')]):
                        results[region_map[product.get('attributes').get('location')]] = set()
                    results[region_map[product.get('attributes').get('location')]].add(
                        product.get('attributes').get('instanceType')
                    )
    return results

def get_redshift_pricing():
    """ Get Redshift Pricing """

    LOGGER.info('Get Redshift pricing')
    paginator = client.get_paginator('get_products')
    page_iterator = paginator.paginate(
        ServiceCode='AmazonRedshift',
        FormatVersion='aws_v1',
    )

    results = {}
    for page in page_iterator:
        for price_item in page.get('PriceList', []):
            products = json.loads(price_item)
            product = products.get('product', {})
            if product:
                if product.get('productFamily') == 'Compute Instance':
                    if not results.get(region_map[product.get('attributes').get('location')]):
                        results[region_map[product.get('attributes').get('location')]] = set()
                    results[region_map[product.get('attributes').get('location')]].add(
                        product.get('attributes').get('instanceType')
                    )
    return results

def get_dax_pricing():
    LOGGER.info('Get DAX pricing')
    paginator = client.get_paginator('get_products')
    page_iterator = paginator.paginate(
        ServiceCode='AmazonDAX',
        FormatVersion='aws_v1',
    )

    results = {}
    for page in page_iterator:
        for price_item in page.get('PriceList', []):
            products = json.loads(price_item)
            product = products.get('product', {})
            if product:
                if product.get('productFamily') == 'DAX':
                    if not results.get(region_map[product.get('attributes').get('location')]):
                        results[region_map[product.get('attributes').get('location')]] = set()
                    usage_type = product.get('attributes').get('usagetype').split(':')[1]
                    results[region_map[product.get('attributes').get('location')]].add(
                        usage_type
                    )
    return results

def get_mq_pricing():
    """ Get MQ Instance Pricing """
    LOGGER.info('Get AmazonMQ pricing')
    paginator = client.get_paginator('get_products')
    page_iterator = paginator.paginate(
        ServiceCode='AmazonMQ',
        FormatVersion='aws_v1',
    )

    remap = {
        'mq.m5.2xl': 'mq.m5.2xlarge',
        'mq.m5.4xl': 'mq.m5.4xlarge'
    }

    results = {}
    for page in page_iterator:
        for price_item in page.get('PriceList', []):
            products = json.loads(price_item)
            product = products.get('product', {})
            if product:
                if product.get('productFamily') == 'Broker Instances':
                    if not results.get(region_map[product.get('attributes').get('location')]):
                        results[region_map[product.get('attributes').get('location')]] = set()
                    usage_type = product.get('attributes').get('usagetype').split(':')[1]
                    results[region_map[product.get('attributes').get('location')]].add(
                        remap.get(usage_type, usage_type)
                    )
    return results

def get_rds_pricing():
    """ Get RDS Pricing """
    LOGGER.info('Get RDS pricing')
    paginator = client.get_paginator('get_products')
    page_iterator = paginator.paginate(
        ServiceCode='AmazonRDS',
        FormatVersion='aws_v1',
    )

    product_map = {
        '2': ['mysql'],
        '3': ['oracle-se1'],
        '4': ['oracle-se'],
        '5': ['oracle-ee'],
        '6': ['oracle-se1'],
        '8': ['sqlserver-se'],
        '9': ['sqlserver-ee'],
        '10': ['sqlserver-ex'],
        '11': ['sqlserver-web'],
        '12': ['sqlserver-se'],
        '14': ['postgres'],
        '15': ['sqlserver-ee'],
        '16': ['aurora-mysql', 'aurora'],
        '18': ['mariadb'],
        '19': ['oracle-se2'],
        '20': ['oracle-se2'],
        '21': ['aurora-postgresql'],
    }

    license_map = {
        'License included': 'license-included',
        'Bring your own license': 'bring-your-own-license',
        'No license required': 'general-public-license'
    }

    rds_specs = {}

    results = {}
    for page in page_iterator:
        for price_item in page.get('PriceList', []):
            products = json.loads(price_item)
            product = products.get('product', {})
            if product:
                if product.get('productFamily') == 'Database Instance':
                    # Get overall instance types
                    if not results.get(region_map[product.get('attributes').get('location')]):
                        results[region_map[product.get('attributes').get('location')]] = set()
                    results[region_map[product.get('attributes').get('location')]].add(
                        product.get('attributes').get('instanceType')
                    )
                    # Rds Instance Size spec
                    product_names = product_map.get(product.get('attributes').get('engineCode'), [])
                    product_region = region_map.get(product.get('attributes').get('location'))
                    license_name = license_map.get(product.get('attributes').get('licenseModel'))
                    instance_type = product.get('attributes').get('instanceType')
                    for product_name in product_names:
                        if not rds_specs.get(license_name):
                            rds_specs[license_name] = {}
                        if not rds_specs.get(license_name).get(product_name):
                            rds_specs[license_name][product_name] = {}
                        if not rds_specs.get(license_name).get(product_name).get(product_region):
                            rds_specs[license_name][product_name][product_region] = set()

                        rds_specs[license_name][product_name][product_region].add(instance_type)

    for license_name, license_values in rds_specs.items():
        for product_name, product_values in license_values.items():
            for product_region, instance_types in product_values.items():
                rds_specs[license_name][product_name][product_region] = list(sorted(instance_types))

    LOGGER.info('Updating RDS Spec files')
    filename = 'src/cfnlint/data/AdditionalSpecs/RdsProperties.json'
    with open(filename, 'w+') as f:
        json.dump(rds_specs, f, indent=2, sort_keys=True, separators=(',', ': '))
    return results

def get_neptune_pricing():
    LOGGER.info('Get Neptune pricing')
    paginator = client.get_paginator('get_products')
    page_iterator = paginator.paginate(
        ServiceCode='AmazonNeptune',
        FormatVersion='aws_v1',
    )

    results = {}
    for page in page_iterator:
        for price_item in page.get('PriceList', []):
            products = json.loads(price_item)
            product = products.get('product', {})
            if product:
                if product.get('productFamily') == 'Database Instance':
                    if not results.get(region_map[product.get('attributes').get('location')]):
                        results[region_map[product.get('attributes').get('location')]] = set()
                    usage_type = product.get('attributes').get('usagetype').split(':')[1]
                    results[region_map[product.get('attributes').get('location')]].add(usage_type)
    return results

def get_documentdb_pricing():
    LOGGER.info('Get DocumentDB pricing')
    paginator = client.get_paginator('get_products')
    page_iterator = paginator.paginate(
        ServiceCode='AmazonDocDB',
        FormatVersion='aws_v1',
    )

    results = {}
    for page in page_iterator:
        for price_item in page.get('PriceList', []):
            products = json.loads(price_item)
            product = products.get('product', {})
            if product:
                if product.get('productFamily') == 'Database Instance':
                    if not results.get(region_map[product.get('attributes').get('location')]):
                        results[region_map[product.get('attributes').get('location')]] = set()
                    results[region_map[product.get('attributes').get('location')]].add(
                        product.get('attributes').get('instanceType')
                    )
    return results

def main():
    """ main function """
    configure_logging()

    outputs = {}
    for region in region_map.values():
        outputs[region] = []

    outputs = update_outputs('Ec2InstanceType', get_ec2_pricing(), outputs)
    outputs = update_outputs('AWS::AmazonMQ::Broker.HostInstanceType', get_mq_pricing(), outputs)
    outputs = update_outputs('RdsInstanceType', get_rds_pricing(), outputs)
    outputs = update_outputs('RedshiftInstanceType', get_redshift_pricing(), outputs)
    outputs = update_outputs('DAXInstanceType', get_dax_pricing(), outputs)
    outputs = update_outputs('DocumentDBInstanceClass', get_documentdb_pricing(), outputs)
    outputs = update_outputs('NeptuneInstanceClass', get_neptune_pricing(), outputs)

    LOGGER.info('Updating spec files')
    for region, patches in outputs.items():
        filename = 'src/cfnlint/data/ExtendedSpecs/%s/05_pricing_property_values.json' % region
        with open(filename, 'w+') as f:
            json.dump(patches, f, indent=2, sort_keys=True, separators=(',', ': '))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, TypeError):
        LOGGER.error(ValueError)
