#!/usr/bin/env python
"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

"""
    Updates our dynamic patches from the pricing API
    This script requires Boto3 and Credentials to call the Pricing API
"""


import json
import logging

import boto3

LOGGER = logging.getLogger('cfnlint')


region_map = {
    'Any': 'all',
    'AWS GovCloud (US-East)': 'us-gov-east-1',
    'AWS GovCloud (US-West)': 'us-gov-west-1',
    'Africa (Cape Town)': 'af-south-1',
    'Asia Pacific (Hong Kong)': 'ap-east-1',
    'Asia Pacific (Jakarta)': 'ap-southeast-3',
    'Asia Pacific (Melbourne)': 'ap-southeast-4',
    'Asia Pacific (Mumbai)': 'ap-south-1',
    'Asia Pacific (Hyderabad)': 'ap-south-2',
    'Asia Pacific (Osaka)': 'ap-northeast-3',
    'Asia Pacific (Osaka-Local)': 'ap-northeast-3',
    'Asia Pacific (Seoul)': 'ap-northeast-2',
    'Asia Pacific (Singapore)': 'ap-southeast-1',
    'Asia Pacific (Sydney)': 'ap-southeast-2',
    'Asia Pacific (Tokyo)': 'ap-northeast-1',
    'Canada (Central)': 'ca-central-1',
    'China (Beijing)': 'cn-north-1',
    'China (Ningxia)': 'cn-northwest-1',
    'EU (Frankfurt)': 'eu-central-1',
    'Europe (Zurich)': 'eu-central-2',
    'EU (Ireland)': 'eu-west-1',
    'EU (London)': 'eu-west-2',
    'EU (Milan)': 'eu-south-1',
    'EU (Paris)': 'eu-west-3',
    'Europe (Spain)': 'eu-south-2',
    'EU (Stockholm)': 'eu-north-1',
    'Middle East (Bahrain)': 'me-south-1',
    'Middle East (UAE)': 'me-central-1',
    'South America (Sao Paulo)': 'sa-east-1',
    'US East (N. Virginia)': 'us-east-1',
    'US East (Ohio)': 'us-east-2',
    'US West (N. California)': 'us-west-1',
    'US West (Oregon)': 'us-west-2',
    'US West (Los Angeles)': 'us-west-2',
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


def get_paginator(service):
    LOGGER.info('Get ' + service + ' pricing paginator')
    return client.get_paginator('get_products').paginate(
        ServiceCode=service,
        FormatVersion='aws_v1',
    )


def get_dax_pricing():
    results = {}
    for page in get_paginator('AmazonDAX'):
        for price_item in page.get('PriceList', []):
            products = json.loads(price_item)
            product = products.get('product', {})
            if product:
                if product.get('productFamily') in ['DAX']:
                    if not results.get(region_map[product.get('attributes').get('location')]):
                        results[region_map[product.get('attributes').get('location')]] = set()
                    results[region_map[product.get('attributes').get('location')]].add(
                        product.get('attributes').get('usagetype').split(':')[1]
                    )
    return results


def get_mq_pricing():
    remap = {
        'mq.m5.2xl': 'mq.m5.2xlarge',
        'mq.m5.4xl': 'mq.m5.4xlarge'
    }
    results = {}
    for page in get_paginator('AmazonMQ'):
        for price_item in page.get('PriceList', []):
            products = json.loads(price_item)
            product = products.get('product', {})
            if product:
                if product.get('productFamily') in ['Broker Instances']:
                    if not results.get(region_map[product.get('attributes').get('location')]):
                        results[region_map[product.get('attributes').get('location')]] = set()
                    usage_type = product.get('attributes').get('usagetype').split(':')[1]
                    results[region_map[product.get('attributes').get('location')]].add(
                        remap.get(usage_type, usage_type)
                    )
    return results


def get_rds_pricing():
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
    for page in get_paginator('AmazonRDS'):
        for price_item in page.get('PriceList', []):
            products = json.loads(price_item)
            product = products.get('product', {})
            if product:
                if product.get('productFamily') in ['Database Instance']:
                    # Get overall instance types
                    if not results.get(region_map[product.get('attributes').get('location')]):
                        results[region_map[product.get('attributes').get('location')]] = set(['db.serverless'])
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
                            if license_name == 'general-public-license' and product_name in ['aurora-mysql', 'aurora-postgresql']:
                                rds_specs[license_name][product_name][product_region] = set(['db.serverless'])
                            else:
                                rds_specs[license_name][product_name][product_region] = set()

                        rds_specs[license_name][product_name][product_region].add(instance_type)

    for license_name, license_values in rds_specs.items():
        for product_name, product_values in license_values.items():
            for product_region, instance_types in product_values.items():
                rds_specs[license_name][product_name][product_region] = list(sorted(instance_types))

    LOGGER.info('Updating RDS Spec files')
    filename = 'src/cfnlint/data/AdditionalSpecs/RdsProperties.json'
    with open(filename, 'w+', encoding='utf-8') as f:
        json.dump(rds_specs, f, indent=1, sort_keys=True, separators=(',', ': '))
    return results


def get_results(service, product_families):
    results = {}
    for page in get_paginator(service):
        for price_item in page.get('PriceList', []):
            products = json.loads(price_item)
            product = products.get('product', {})
            if product:
                if product.get('productFamily') in product_families and product.get('attributes').get('locationType') == "AWS Region":
                    if product.get('attributes').get('location') not in region_map:
                        LOGGER.warning('Region "%s" not found', product.get('attributes').get('location'))
                        continue
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

    outputs = update_outputs('Ec2InstanceType', get_results('AmazonEC2', ['Compute Instance', 'Compute Instance (bare metal)']), outputs)
    outputs = update_outputs('AWS::AmazonMQ::Broker.HostInstanceType', get_mq_pricing(), outputs)
    outputs = update_outputs('AWS::RDS::DBInstance.DBInstanceClass', get_rds_pricing(), outputs)
    outputs = update_outputs('RedshiftInstanceType', get_results('AmazonRedshift', ['Compute Instance']), outputs)
    outputs = update_outputs('DAXInstanceType', get_dax_pricing(), outputs)
    outputs = update_outputs('DocumentDBInstanceClass', get_results('AmazonDocDB', ['Database Instance']), outputs)
    outputs = update_outputs('NeptuneInstanceClass', get_results('AmazonNeptune', ['Database Instance']), outputs)
    outputs = update_outputs('ElastiCacheInstanceType', get_results('AmazonElastiCache', ['Cache Instance']), outputs)
    outputs = update_outputs('ElasticsearchInstanceType', get_results('AmazonES', ['Elastic Search Instance']), outputs)
    outputs = update_outputs('EMRInstanceType', get_results('ElasticMapReduce', ['Elastic Map Reduce Instance']), outputs)
    outputs = update_outputs('BlockchainInstanceType', get_results('AmazonManagedBlockchain', ['Blockchain Instance']), outputs)
    outputs = update_outputs('AWS::GameLift::Fleet.EC2InstanceType', get_results('AmazonGameLift', ['GameLift EC2 Instance']), outputs)
    outputs = update_outputs('AppStreamInstanceType', get_results('AmazonAppStream', ['Streaming Instance']), outputs)

    LOGGER.info('Updating spec files')
    for region, patches in outputs.items():
        filename = 'src/cfnlint/data/ExtendedSpecs/%s/05_pricing_property_values.json' % region
        with open(filename, 'w+', encoding='utf-8') as f:
            json.dump(patches, f, indent=1, sort_keys=True, separators=(',', ': '))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, TypeError):
        LOGGER.error(ValueError)
