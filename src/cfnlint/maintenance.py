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
import pkg_resources
import requests

import cfnlint

LOGGER = logging.getLogger('cfnlint')


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
        with open(filename, 'wb') as f:
            f.write(req.content)


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
