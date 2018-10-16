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
import logging
import json
import requests
import pkg_resources
import jsonpointer
import jsonpatch
import cfnlint

LOGGER = logging.getLogger(__name__)


def update_resource_specs():
    """ Update Resource Specs """

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
        content = json.loads(req.content)
        content = patch_spec(content, region)
        with open(filename, 'w') as f:
            json.dump(content, f, indent=2)


def update_documentation(rules):
    """Generate documentation"""

    # Update the overview of all rules in the linter
    filename = 'docs/rules.md'

    # Sort rules by the Rule ID
    sorted_rules = sorted(rules, key=lambda obj: obj.id)

    data = []

    # Read current file up to the Rules part, everything up to that point is
    # static documentation.
    with open(filename, 'r') as origial_file:

        line = origial_file.readline()
        while line:
            data.append(line)

            if line == '## Rules\n':
                break

            line = origial_file.readline()

    # Rebuild the file content
    with open(filename, 'w') as new_file:

        # Rewrite the static documentation
        for line in data:
            new_file.write(line)

        # Add the rules
        new_file.write('The following **{}** rules are applied by this linter:\n\n'.format(len(sorted_rules)))
        new_file.write('| Rule ID  | Title | Description | Source | Tags |\n')
        new_file.write('| -------- | ----- | ----------- | ------ | ---- |\n')

        rule_output = '| {0} <a name="{0}"></a> | {1} | {2} | [Source]({3}) | {4} |\n'

        # Add system Errors (hardcoded)
        parseerror = cfnlint.ParseError()
        tags = ','.join('`{0}`'.format(tag) for tag in parseerror.tags)
        new_file.write(rule_output.format(
            parseerror.id, parseerror.shortdesc, parseerror.description, '', tags))

        transformerror = cfnlint.TransformError()
        tags = ','.join('`{0}`'.format(tag) for tag in transformerror.tags)
        new_file.write(rule_output.format(
            transformerror.id, transformerror.shortdesc, transformerror.description, '', tags))

        ruleerror = cfnlint.RuleError()
        tags = ','.join('`{0}`'.format(tag) for tag in ruleerror.tags)
        new_file.write(
            rule_output.format(ruleerror.id, ruleerror.shortdesc, ruleerror.description, '', tags))

        for rule in sorted_rules:
            tags = ','.join('`{0}`'.format(tag) for tag in rule.tags)
            new_file.write(rule_output.format(rule.id, rule.shortdesc, rule.description, rule.source_url, tags))


def patch_spec(content, region):
    """Patch the spec file"""
    json_patches = [
        # CloudFront DistributionConfig Origin and DefaultCacheBehavior
        {
            'Name': 'Origin and DefaultCacheBehavior required for AWS::CloudFront::Distribution.DistributionConfig',
            'Regions': ['All'],
            'Patch': jsonpatch.JsonPatch([
                {'op': 'replace', 'path': '/PropertyTypes/AWS::CloudFront::Distribution.DistributionConfig/Properties/DefaultCacheBehavior/Required', 'value': True},
                {'op': 'replace', 'path': '/PropertyTypes/AWS::CloudFront::Distribution.DistributionConfig/Properties/Origins/Required', 'value': True},
            ])
        },
        # VPC Endpoint and DNS Endpoint
        {
            'Name': 'VpcEndpointType in AWS::EC2::VPCEndpoint',
            'Regions': ['All'],
            'Patch': jsonpatch.JsonPatch([
                {'op': 'move', 'from': '/ResourceTypes/AWS::EC2::VPCEndpoint/Properties/VPCEndpointType', 'path': '/ResourceTypes/AWS::EC2::VPCEndpoint/Properties/VpcEndpointType'}
            ])
        },
        # RDS AutoScaling
        {
            'Name': 'RDS AutoScaling Pause',
            'Regions': ['All'],
            'Patch': jsonpatch.JsonPatch([
                {'op': 'move', 'from': '/PropertyTypes/AWS::RDS::DBCluster.ScalingConfiguration/Properties/SecondsBeforeAutoPause', 'path': '/PropertyTypes/AWS::RDS::DBCluster.ScalingConfiguration/Properties/SecondsUntilAutoPause'}
            ])
        },
        {
            'Name': 'AWS::CloudFormation::WaitCondition has no required properties',
            'Regions': ['All'],
            'Patch': jsonpatch.JsonPatch([
                {'op': 'replace', 'path': '/ResourceTypes/AWS::CloudFormation::WaitCondition/Properties/Handle/Required', 'value': False},
                {'op': 'replace', 'path': '/ResourceTypes/AWS::CloudFormation::WaitCondition/Properties/Timeout/Required', 'value': False},
            ])
        },
        {
            'Name': 'AWS::EC2::SpotFleet.SpotFleetTagSpecification supports Tags',
            'Regions': ['All'],
            'Patch': jsonpatch.JsonPatch([
                {'op': 'add', 'path': '/PropertyTypes/AWS::EC2::SpotFleet.SpotFleetTagSpecification/Properties/Tags', 'value': {
                    'Type': 'List',
                    'Required': False,
                    'Documentation': 'http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ec2-spotfleet-spotfleetrequestconfigdata-launchspecifications-tagspecifications.html#cfn-ec2-spotfleet-spotfleettagspecification-tags',
                    'ItemType': 'Tag',
                    'UpdateType': 'Mutable'
                }}
            ])
        },
        {
            'Name': 'AWS::Cognito::UserPool.SmsConfiguration ExternalId IS required',
            'Regions': ['All'],
            'Patch': jsonpatch.JsonPatch([
                {'op': 'replace', 'path': '/PropertyTypes/AWS::Cognito::UserPool.SmsConfiguration/Properties/ExternalId/Required', 'value': True}
            ])
        },
        {
            'Name': 'Add type AWS::SSM::MaintenanceWindow',
            'Regions': ['All'],  # need to double check this
            'Patch': jsonpatch.JsonPatch([
                {
                    'op': 'add', 'path': '/ResourceTypes/AWS::SSM::MaintenanceWindow',
                    'value': {
                        'Documentation': 'http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindow.html',
                        'Properties': {
                            'Description': {
                                'Required': False,
                                'Documentation': 'http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindow.html#cfn-ssm-maintenancewindow-description',
                                'PrimitiveType': 'String',
                                'UpdateType': 'Mutable'
                            },
                            'AllowUnassociatedTargets': {
                                'Required': True,
                                'Documentation': 'http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindow.html#cfn-ssm-maintenancewindow-allowunassociatedtargets',
                                'PrimitiveType': 'Boolean',
                                'UpdateType': 'Mutable'
                            },
                            'Cutoff': {
                                'Required': True,
                                'Documentation': 'http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindow.html#cfn-ssm-maintenancewindow-cutoff',
                                'PrimitiveType': 'Integer',
                                'UpdateType': 'Mutable'
                            },
                            'Schedule': {
                                'Required': True,
                                'Documentation': 'http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindow.html#cfn-ssm-maintenancewindow-schedule',
                                'PrimitiveType': 'String',
                                'UpdateType': 'Mutable'
                            },
                            'Duration': {
                                'Required': True,
                                'Documentation': 'http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindow.html#cfn-ssm-maintenancewindow-duration',
                                'PrimitiveType': 'Integer',
                                'UpdateType': 'Mutable'
                            },
                            'Name': {
                                'Required': True,
                                'Documentation': 'http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindow.html#cfn-ssm-maintenancewindow-name',
                                'PrimitiveType': 'String',
                                'UpdateType': 'Mutable'
                            }
                        }
                    }
                }
            ])
        },
        {
            'Name': 'Add type AWS::SSM::MaintenanceWindowTarget',
            'Regions': ['All'],  # need to double check this
            'Patch': jsonpatch.JsonPatch([
                {
                    'op': 'add', 'path': '/ResourceTypes/AWS::SSM::MaintenanceWindowTarget',
                    'value': {
                        'Documentation': 'http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindowtarget.html',
                        'Properties': {
                            'OwnerInformation': {
                                'Required': False,
                                'Documentation': 'http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindowtarget.html#cfn-ssm-maintenancewindowtarget-ownerinformation',
                                'PrimitiveType': 'String',
                                'UpdateType': 'Mutable'
                            },
                            'Description': {
                                'Required': False,
                                'Documentation': 'http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindowtarget.html#cfn-ssm-maintenancewindowtarget-description',
                                'PrimitiveType': 'String',
                                'UpdateType': 'Mutable'
                            },
                            'WindowId': {
                                'Required': True,
                                'Documentation': 'http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindowtarget.html#cfn-ssm-maintenancewindowtarget-windowid',
                                'PrimitiveType': 'String',
                                'UpdateType': 'Mutable'
                            },
                            'ResourceType': {
                                'Required': True,
                                'Documentation': 'http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindowtarget.html#cfn-ssm-maintenancewindowtarget-resourcetype',
                                'PrimitiveType': 'String',
                                'UpdateType': 'Mutable'
                            },
                            'Targets': {
                                'Required': True,
                                'Documentation': 'http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindowtarget.html#cfn-ssm-maintenancewindowtarget-targets',
                                'PrimitiveType': 'String',
                                'Type': 'List',
                                'ItemType': 'Target',
                                'UpdateType': 'Mutable'
                            },
                            'Name': {
                                'Required': False,
                                'Documentation': 'http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindowtarget.html#cfn-ssm-maintenancewindowtarget-name',
                                'PrimitiveType': 'String',
                                'UpdateType': 'Mutable'
                            },
                        }
                    }
                },
                {
                    'op': 'add', 'path': '/PropertyTypes/AWS::SSM::MaintenanceWindowTarget.Target',
                    'value': {
                        'Documentation': 'http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-maintenancewindowtarget.html',
                        'Properties': {
                            'Key': {
                                'Required': True,
                                'Documentation': 'http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtarget-targets.html#cfn-ssm-maintenancewindowtarget-targets-key',
                                'PrimitiveType': 'String',
                                'UpdateType': 'Mutable'
                            },
                            'Values': {
                                'Required': False,
                                'Documentation': 'http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-ssm-maintenancewindowtarget-targets.html#cfn-ssm-maintenancewindowtarget-targets-values',
                                'PrimitiveItemType': 'String',
                                'UpdateType': 'Mutable',
                                'Type': 'List',
                            },
                        }
                    }
                }
            ])
        },
        {
            'Name': 'AWS::SNS::Subscription TopicArn and Protocol IS required',
            'Regions': ['All'],
            'Patch': jsonpatch.JsonPatch([
                {'op': 'replace', 'path': '/ResourceTypes/AWS::SNS::Subscription/Properties/TopicArn/Required', 'value': True},
                {'op': 'replace', 'path': '/ResourceTypes/AWS::SNS::Subscription/Properties/Protocol/Required', 'value': True}
            ])
        },
        {
            'Name': 'AWS::SDB::Domain not supported for all regions',
            'Regions': ['us-east-2', 'ca-central-1', 'eu-central-1', 'eu-west-2', 'eu-west-3', 'ap-northeast-2', 'ap-south-1'],
            'Patch': jsonpatch.JsonPatch([
                {'op': 'remove', 'path': '/ResourceTypes/AWS::SDB::Domain'}
            ])
        },
    ]

    for json_patch in json_patches:
        for patch_region in json_patch.get('Regions'):
            if patch_region in [region, 'All']:
                try:
                    json_patch.get('Patch').apply(content, in_place=True)
                    break  # only need to patch once
                except jsonpatch.JsonPatchConflict:
                    LOGGER.info('Patch not applied: %s in region %s', json_patch.get('Name'), region)
                except jsonpointer.JsonPointerException:
                    # Debug as the parent element isn't supported in the region
                    LOGGER.debug('Parent element not found for patch: %s in region %s', json_patch.get('Name'), region)

    return content
