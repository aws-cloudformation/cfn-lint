"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import re
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class SubNeeded(CloudFormationLintRule):
    """Check if a substitution string exists without a substitution function"""
    id = 'E1029'
    shortdesc = 'Sub is required if a variable is used in a string'
    description = 'If a substitution variable exists in a string but isn\'t wrapped with the Fn::Sub function the deployment will fail.'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-sub.html'
    tags = ['functions', 'sub']

    # Free-form text properties to exclude from this rule
    # content is part of AWS::CloudFormation::Init
    excludes = ['UserData', 'ZipFile', 'Condition', 'AWS::CloudFormation::Init',
                'CloudWatchAlarmDefinition', 'TopicRulePayload']
    api_excludes = ['Uri', 'Body']

    # IAM Policy has special variables that don't require !Sub, Check for these
    # https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_variables.html
    # https://docs.aws.amazon.com/iot/latest/developerguide/basic-policy-variables.html
    # https://docs.aws.amazon.com/iot/latest/developerguide/thing-policy-variables.html
    # https://docs.aws.amazon.com/transfer/latest/userguide/users.html#users-policies-scope-down
    # https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_iam-condition-keys.html
    resource_excludes = ['${aws:CurrentTime}', '${aws:EpochTime}',
                         '${aws:TokenIssueTime}', '${aws:principaltype}',
                         '${aws:SecureTransport}', '${aws:SourceIp}',
                         '${aws:UserAgent}', '${aws:userid}',
                         '${aws:username}', '${ec2:SourceInstanceARN}',
                         '${iot:Connection.Thing.ThingName}',
                         '${iot:Connection.Thing.ThingTypeName}',
                         '${iot:Connection.Thing.IsAttached}',
                         '${iot:ClientId}', '${transfer:HomeBucket}',
                         '${transfer:HomeDirectory}', '${transfer:HomeFolder}',
                         '${transfer:UserName}', '${redshift:DbUser}',
                         '${cognito-identity.amazonaws.com:aud}',
                         '${cognito-identity.amazonaws.com:sub}',
                         '${cognito-identity.amazonaws.com:amr}']

    # https://docs.aws.amazon.com/redshift/latest/mgmt/redshift-iam-access-control-identity-based.html
    condition_excludes = [
        '${redshift:DbUser}',
    ]

    def __init__(self):
        """Init"""
        super(SubNeeded, self).__init__()
        self.config_definition = {
            'custom_excludes': {
                'default': '',
                'type': 'string'
            }
        }
        self.configure()

    def _match_values(self, searchRegex, cfnelem, path):
        """Recursively search for values matching the searchRegex"""
        values = []
        if isinstance(cfnelem, dict):
            for key in cfnelem:
                pathprop = path[:]
                pathprop.append(key)
                values.extend(self._match_values(searchRegex, cfnelem[key], pathprop))
        elif isinstance(cfnelem, list):
            for index, item in enumerate(cfnelem):
                pathprop = path[:]
                pathprop.append(index)
                values.extend(self._match_values(searchRegex, item, pathprop))
        else:
            # Leaf node
            if isinstance(cfnelem, str) and re.match(searchRegex, cfnelem):
                # Get all variables as seperate paths
                regex = re.compile(r'(\$\{.*?\.?.*?})')
                for variable in re.findall(regex, cfnelem):
                    values.append(path + [variable])

        return values

    def match_values(self, searchRegex, cfn):
        """
            Search for values in all parts of the templates that match the searchRegex
        """
        results = []
        results.extend(self._match_values(searchRegex, cfn.template, []))
        # Globals are removed during a transform.  They need to be checked manually
        results.extend(self._match_values(searchRegex, cfn.template.get('Globals', {}), []))
        return results

    def _api_exceptions(self, value):
        """ Key value exceptions """
        parameter_search = re.compile(r'^\$\{stageVariables\..*\}$')
        return re.match(parameter_search, value)

    def _variable_custom_excluded(self, value):
        """ User-defined exceptions for variables, anywhere in the file """
        custom_excludes = self.config['custom_excludes']
        if custom_excludes:
            custom_search = re.compile(custom_excludes)
            return re.match(custom_search, value)
        return False

    def match(self, cfn):
        """Basic Rule Matching"""

        matches = []

        # Generic regex to match a string containing at least one ${parameter}
        parameter_search = re.compile(r'^.*(\$\{.*\}.*(\$\{.*\}.*)*)$')

        # Get a list of paths to every leaf node string containing at least one ${parameter}
        parameter_string_paths = self.match_values(parameter_search, cfn)

        # We want to search all of the paths to check if each one contains an 'Fn::Sub'
        for parameter_string_path in parameter_string_paths:
            if parameter_string_path[0] in ['Parameters']:
                continue
            # Exclude the special IAM variables
            variable = parameter_string_path[-1]

            if 'Resource' in parameter_string_path:
                if variable in self.resource_excludes:
                    continue
            if 'NotResource' in parameter_string_path:
                if variable in self.resource_excludes:
                    continue
            if 'Condition' in parameter_string_path:
                if variable in self.condition_excludes:
                    continue

            # Exclude variables that match custom exclude filters, if configured
            # (for third-party tools that pre-process templates before uploading them to AWS)
            if self._variable_custom_excluded(variable):
                continue

            # Exclude literals (https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-sub.html)
            if variable.startswith('${!'):
                continue

            found_sub = False
            # Does the path contain an 'Fn::Sub'?
            for step in parameter_string_path:
                if step in self.api_excludes:
                    if self._api_exceptions(parameter_string_path[-1]):
                        found_sub = True
                elif step == 'Fn::Sub' or step in self.excludes:
                    found_sub = True

            # If we didn't find an 'Fn::Sub' it means a string containing a ${parameter} may not be evaluated correctly
            if not found_sub:
                # Remove the last item (the variable) to prevent multiple errors on 1 line errors
                path = parameter_string_path[:-1]
                message = 'Found an embedded parameter outside of an "Fn::Sub" at {}'.format(
                    '/'.join(map(str, path)))
                matches.append(RuleMatch(path, message))

        return matches
