"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import datetime
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class Base(CloudFormationLintRule):
    """Check Base Template Settings"""
    id = 'E1001'
    shortdesc = 'Basic CloudFormation Template Configuration'
    description = 'Making sure the basic CloudFormation template components are properly configured'
    source_url = 'https://github.com/aws-cloudformation/cfn-python-lint'
    tags = ['base']

    required_keys = [
        'Resources'
    ]

    def __init__(self):
        """Init"""
        super(Base, self).__init__()
        self.config_definition = {
            'sections': {
                'default': '',
                'type': 'string'
            }
        }
        self.configure()

    def _validate_version(self, template):
        results = []
        valid_version = '2010-09-09'
        if 'AWSTemplateFormatVersion' in template:
            version = template.get('AWSTemplateFormatVersion')
            if not isinstance(version, (str, datetime.date)):
                message = 'AWSTemplateFormatVersion only valid value is {0}'
                results.append(RuleMatch(['AWSTemplateFormatVersion'], message.format(valid_version)))
            else:
                if version != valid_version and version != datetime.datetime.strptime(valid_version, '%Y-%m-%d').date():
                    message = 'AWSTemplateFormatVersion only valid value is {0}'
                    results.append(RuleMatch(['AWSTemplateFormatVersion'], message.format(valid_version)))
        return results

    def _validate_transform(self, transforms):
        results = []
        if not isinstance(transforms, (list, str)):
            message = 'Transform has to be a list or string'
            results.append(RuleMatch(['Transform'], message.format()))
            return results

        if not isinstance(transforms, list):
            transforms = [transforms]

        return results

    def match(self, cfn):
        matches = []

        top_level = []
        for x in cfn.template:
            top_level.append(x)
            if x not in cfn.sections and x != self.config['sections']:
                message = 'Top level template section {0} is not valid'
                matches.append(RuleMatch([x], message.format(x)))

        for y in self.required_keys:
            if y not in top_level:
                message = 'Missing top level template section {0}'
                matches.append(RuleMatch([y], message.format(y)))

        matches.extend(self._validate_version(cfn.template))
        if 'Transform' in cfn.template:
            matches.extend(self._validate_transform(cfn.template.get('Transform')))
        return matches
