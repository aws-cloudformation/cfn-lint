"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import fnmatch
import json
import logging
import os
import jsonpointer
import jsonpatch
import cfnlint
from cfnlint.helpers import get_url_content
import cfnlint.data.ExtendedSpecs


LOGGER = logging.getLogger(__name__)


SPEC_REGIONS = {
    'ap-east-1': 'https://cfn-resource-specifications-ap-east-1-prod.s3.ap-east-1.amazonaws.com/latest/gzip/CloudFormationResourceSpecification.json',
    'ap-northeast-1': 'https://d33vqc0rt9ld30.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json',
    'ap-northeast-2': 'https://d1ane3fvebulky.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json',
    'ap-northeast-3': 'https://d2zq80gdmjim8k.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json',
    'ap-south-1': 'https://d2senuesg1djtx.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json',
    'ap-southeast-1': 'https://doigdx0kgq9el.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json',
    'ap-southeast-2': 'https://d2stg8d246z9di.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json',
    'ca-central-1': 'https://d2s8ygphhesbe7.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json',
    'cn-north-1': 'https://cfn-resource-specifications-cn-north-1-prod.s3.cn-north-1.amazonaws.com.cn/latest/gzip/CloudFormationResourceSpecification.json',
    'cn-northwest-1': 'https://cfn-resource-specifications-cn-northwest-1-prod.s3.cn-northwest-1.amazonaws.com.cn/latest/gzip/CloudFormationResourceSpecification.json',
    'eu-central-1': 'https://d1mta8qj7i28i2.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json',
    'eu-north-1': 'https://diy8iv58sj6ba.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json',
    'eu-west-1': 'https://d3teyb21fexa9r.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json',
    'eu-west-2': 'https://d1742qcu2c1ncx.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json',
    'eu-west-3': 'https://d2d0mfegowb3wk.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json',
    'me-south-1': 'https://cfn-resource-specifications-me-south-1-prod.s3.me-south-1.amazonaws.com/latest/gzip/CloudFormationResourceSpecification.json',
    'sa-east-1': 'https://d3c9jyj3w509b0.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json',
    'us-east-1': 'https://d1uauaxba7bl26.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json',
    'us-east-2': 'https://dnwj8swjjbsbt.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json',
    'us-gov-east-1': 'https://s3.us-gov-east-1.amazonaws.com/cfn-resource-specifications-us-gov-east-1-prod/latest/gzip/CloudFormationResourceSpecification.json',
    'us-gov-west-1': 'https://s3.us-gov-west-1.amazonaws.com/cfn-resource-specifications-us-gov-west-1-prod/latest/gzip/CloudFormationResourceSpecification.json',
    'us-west-1': 'https://d68hl49wbnanq.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json',
    'us-west-2': 'https://d201a2mn26r7lk.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json',
}


def update_resource_specs():
    """ Update Resource Specs """

    for region, url in SPEC_REGIONS.items():
        filename = os.path.join(os.path.dirname(cfnlint.__file__),
                                'data/CloudSpecs/%s.json' % region)
        LOGGER.debug('Downloading template %s into %s', url, filename)
        spec = json.loads(get_url_content(url))

        # Patch the files
        spec = patch_spec(spec, 'all')
        spec = patch_spec(spec, region)

        with open(filename, 'w') as f:
            json.dump(spec, f, indent=2, sort_keys=True, separators=(',', ': '))


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
        new_file.write(
            'The following **{}** rules are applied by this linter:\n'.format(len(sorted_rules)))
        new_file.write(
            '(_This documentation is generated from the Rules, do not alter this manually_)\n\n')
        new_file.write(
            '| Rule ID  | Title | Description | Config<br />(Name:Type:Default) | Source | Tags |\n')
        new_file.write('| -------- | ----- | ----------- | ---------- | ------ | ---- |\n')

        rule_output = '| {0}<a name="{0}"></a> | {1} | {2} | {3} | [Source]({4}) | {5} |\n'

        # Add system Errors (hardcoded)
        parseerror = cfnlint.rules.ParseError()
        tags = ','.join('`{0}`'.format(tag) for tag in parseerror.tags)
        new_file.write(rule_output.format(
            parseerror.id, parseerror.shortdesc, parseerror.description, '', '', tags))

        transformerror = cfnlint.rules.TransformError()
        tags = ','.join('`{0}`'.format(tag) for tag in transformerror.tags)
        new_file.write(rule_output.format(
            transformerror.id, transformerror.shortdesc, transformerror.description, '', '', tags))

        ruleerror = cfnlint.rules.RuleError()
        tags = ','.join('`{0}`'.format(tag) for tag in ruleerror.tags)
        new_file.write(
            rule_output.format(ruleerror.id, ruleerror.shortdesc, ruleerror.description, '', '', tags))

        # Seprate the experimental rules
        experimental_rules = []

        for rule in sorted_rules:

            if rule.experimental:
                experimental_rules.append(rule)
                continue

            tags = ','.join('`{0}`'.format(tag) for tag in rule.tags)
            config = '<br />'.join('{0}:{1}:{2}'.format(key, values.get('type'), values.get('default'))
                                   for key, values in rule.config_definition.items())
            new_file.write(rule_output.format(rule.id, rule.shortdesc,
                                              rule.description, config, rule.source_url, tags))

        # Output the experimental rules (if any)
        if experimental_rules:
            new_file.write('### Experimental rules\n')
            new_file.write('| Rule ID  | Title | Description | Source | Tags |\n')
            new_file.write('| -------- | ----- | ----------- | ------ | ---- |\n')

            for rule in experimental_rules:
                tags = ','.join('`{0}`'.format(tag) for tag in rule.tags)
                config = '<br />'.join('{0}:{1}:{2}'.format(key, values.get('type'), values.get('default'))
                                       for key, values in rule.config_definition.items())
                new_file.write(rule_output.format(rule.id, rule.shortdesc,
                                                  rule.description, config, rule.source_url, tags))


def patch_spec(content, region):
    """Patch the spec file"""
    LOGGER.info('Patching spec file for region "%s"', region)

    append_dir = os.path.join(os.path.dirname(__file__), 'data', 'ExtendedSpecs', region)
    for dirpath, _, filenames in os.walk(append_dir):
        filenames.sort()
        for filename in fnmatch.filter(filenames, '*.json'):
            file_path = os.path.basename(filename)
            module = dirpath.replace('%s' % append_dir, '%s' % region).replace('/', '.')
            LOGGER.info('Processing %s/%s', module, file_path)
            all_patches = jsonpatch.JsonPatch(cfnlint.helpers.load_resource(
                'cfnlint.data.ExtendedSpecs.{}'.format(module), file_path))

            # Process the generic patches 1 by 1 so we can "ignore" failed ones
            for all_patch in all_patches:
                try:
                    jsonpatch.JsonPatch([all_patch]).apply(content, in_place=True)
                except jsonpatch.JsonPatchConflict:
                    LOGGER.debug('Patch (%s) not applied in region %s', all_patch, region)
                except jsonpointer.JsonPointerException:
                    # Debug as the parent element isn't supported in the region
                    LOGGER.debug('Parent element not found for patch (%s) in region %s',
                                 all_patch, region)

    return content


def update_iam_policies():
    """update iam policies file"""

    url = 'https://awspolicygen.s3.amazonaws.com/js/policies.js'

    filename = os.path.join(
        os.path.dirname(cfnlint.data.AdditionalSpecs.__file__),
        'Policies.json')
    LOGGER.debug('Downloading policies %s into %s', url, filename)

    content = get_url_content(url)

    content = content.split('app.PolicyEditorConfig=')[1]
    content = json.loads(content)
    content['serviceMap']['Manage Amazon API Gateway']['Actions'].extend(
        ['HEAD', 'OPTIONS']
    )
    content['serviceMap']['Amazon Kinesis Video Streams']['Actions'].append(
        'StartStreamEncryption'
    )

    with open(filename, 'w') as f:
        json.dump(content, f, indent=2, sort_keys=True, separators=(',', ': '))
