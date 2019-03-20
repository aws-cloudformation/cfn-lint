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
import fnmatch
import json
import logging
import os
import requests
import pkg_resources
import jsonpointer
import jsonpatch
import cfnlint

LOGGER = logging.getLogger(__name__)


def update_resource_specs():
    """ Update Resource Specs """

    regions = {
        'ap-northeast-1': 'https://d33vqc0rt9ld30.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json',
        'ap-northeast-2': 'https://d1ane3fvebulky.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json',
        'ap-northeast-3': 'https://d2zq80gdmjim8k.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json',
        'ap-south-1': 'https://d2senuesg1djtx.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json',
        'ap-southeast-1': 'https://doigdx0kgq9el.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json',
        'ap-southeast-2': 'https://d2stg8d246z9di.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json',
        'ca-central-1': 'https://d2s8ygphhesbe7.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json',
        'eu-central-1': 'https://d1mta8qj7i28i2.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json',
        'eu-north-1': 'https://diy8iv58sj6ba.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json',
        'eu-west-1': 'https://d3teyb21fexa9r.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json',
        'eu-west-2': 'https://d1742qcu2c1ncx.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json',
        'eu-west-3': 'https://d2d0mfegowb3wk.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json',
        'sa-east-1': 'https://d3c9jyj3w509b0.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json',
        'us-east-1': 'https://d1uauaxba7bl26.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json',
        'us-east-2': 'https://dnwj8swjjbsbt.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json',
        'us-west-1': 'https://d68hl49wbnanq.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json',
        'us-west-2': 'https://d201a2mn26r7lk.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json',
        'us-gov-east-1': 'https://s3.us-gov-east-1.amazonaws.com/cfn-resource-specifications-us-gov-east-1-prod/latest/CloudFormationResourceSpecification.json',
        'us-gov-west-1': 'https://s3.us-gov-west-1.amazonaws.com/cfn-resource-specifications-us-gov-west-1-prod/latest/CloudFormationResourceSpecification.json'
    }

    for region, url in regions.items():
        filename = pkg_resources.resource_filename(
            __name__,
            '/data/CloudSpecs/%s.json' % region,
        )
        LOGGER.debug('Downloading template %s into %s', url, filename)
        req = requests.get(url)

        content = json.loads(req.content.decode('utf-8'))

        # Patch the files
        content = patch_spec(content, 'all')
        content = patch_spec(content, region)

        with open(filename, 'w') as f:
            json.dump(content, f, indent=2, sort_keys=True, separators=(',', ': '))


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

        rule_output = '| {0}<a name="{0}"></a> | {1} | {2} | [Source]({3}) | {4} |\n'

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

        # Seprate the experimental rules
        experimental_rules = []

        for rule in sorted_rules:

            if rule.experimental:
                experimental_rules.append(rule)
                continue

            tags = ','.join('`{0}`'.format(tag) for tag in rule.tags)
            new_file.write(rule_output.format(rule.id, rule.shortdesc, rule.description, rule.source_url, tags))

        # Output the experimental rules (if any)
        if experimental_rules:
            new_file.write('### Experimental rules\n')
            new_file.write('| Rule ID  | Title | Description | Source | Tags |\n')
            new_file.write('| -------- | ----- | ----------- | ------ | ---- |\n')

            for rule in experimental_rules:
                tags = ','.join('`{0}`'.format(tag) for tag in rule.tags)
                new_file.write(rule_output.format(rule.id, rule.shortdesc, rule.description, rule.source_url, tags))

def patch_spec(content, region):
    """Patch the spec file"""
    LOGGER.info('Patching spec file for region "%s"', region)

    append_dir = os.path.join(os.path.dirname(__file__), 'data', 'ExtendedSpecs', region)
    for _, _, filenames in os.walk(append_dir):
        filenames.sort()
        for filename in fnmatch.filter(filenames, '*.json'):
            LOGGER.info('Processing %s (%s)', filename, region)
            all_patches = jsonpatch.JsonPatch(cfnlint.helpers.load_resources('data/ExtendedSpecs/{}/{}'.format(region, filename)))

            # Process the generic patches 1 by 1 so we can "ignore" failed ones
            for all_patch in all_patches:
                try:
                    jsonpatch.JsonPatch([all_patch]).apply(content, in_place=True)
                except jsonpatch.JsonPatchConflict:
                    LOGGER.debug('Patch (%s) not applied in region %s', all_patch, region)
                except jsonpointer.JsonPointerException:
                    # Debug as the parent element isn't supported in the region
                    LOGGER.debug('Parent element not found for patch (%s) in region %s', all_patch, region)

    return content

def update_iam_policies():
    """update iam policies file"""

    url = 'https://awspolicygen.s3.amazonaws.com/js/policies.js'

    filename = pkg_resources.resource_filename(
        __name__,
        '/data/AdditionalSpecs/Policies.json',
    )
    LOGGER.debug('Downloading policies %s into %s', url, filename)

    req = requests.get(url)

    content = req.content.decode('utf-8')

    content = content.split('app.PolicyEditorConfig=')[1]
    content = json.loads(content)
    content['serviceMap']['Manage Amazon API Gateway']['Actions'].extend(['HEAD', 'OPTIONS'])
    content['serviceMap']['Amazon Kinesis Video Streams']['Actions'].append('StartStreamEncryption')

    with open(filename, 'w') as f:
        json.dump(content, f, indent=2, sort_keys=True, separators=(',', ': '))
