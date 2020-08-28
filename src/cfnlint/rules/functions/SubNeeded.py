"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from functools import reduce  # pylint: disable=redefined-builtin
import re
import six
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
    excludes = ['UserData', 'ZipFile', 'Condition', 'AWS::CloudFormation::Init',
                'CloudWatchAlarmDefinition', 'TopicRulePayload', 'BuildSpec',
                'RequestMappingTemplate', 'LogFormat', 'TemplateBody', 'ResponseMappingTemplate']
    api_excludes = ['Uri', 'Body', 'ConnectionId']


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
        self.subParameterRegex = re.compile(r'(\$\{[A-Za-z0-9_:\.]+\})')

    def _match_values(self, cfnelem, path):
        """Recursively search for values matching the searchRegex"""
        values = []
        if isinstance(cfnelem, dict):
            for key in cfnelem:
                pathprop = path[:]
                pathprop.append(key)
                values.extend(self._match_values(cfnelem[key], pathprop))
        elif isinstance(cfnelem, list):
            for index, item in enumerate(cfnelem):
                pathprop = path[:]
                pathprop.append(index)
                values.extend(self._match_values(item, pathprop))
        else:
            # Leaf node
            if isinstance(cfnelem, six.string_types):  # and re.match(searchRegex, cfnelem):
                for variable in re.findall(self.subParameterRegex, cfnelem):
                    values.append(path + [variable])

        return values

    def match_values(self, cfn):
        """
            Search for values in all parts of the templates that match the searchRegex
        """
        results = []
        results.extend(self._match_values(cfn.template, []))
        # Globals are removed during a transform.  They need to be checked manually
        results.extend(self._match_values(cfn.template.get('Globals', {}), []))
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
        matches = []

        # Get a list of paths to every leaf node string containing at least one ${parameter}
        parameter_string_paths = self.match_values(cfn)
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

            # Step Function State Machine has a Definition Substitution that allows usage of special variables outside of a !Sub
            # https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-stepfunctions-statemachine-definitionsubstitutions.html

            if 'DefinitionString' in parameter_string_path:
                modified_parameter_string_path = parameter_string_path
                index = parameter_string_path.index('DefinitionString')
                modified_parameter_string_path[index] = 'DefinitionSubstitutions'
                modified_parameter_string_path = modified_parameter_string_path[:index+1]
                modified_parameter_string_path.append(variable[2:-1])
                if reduce(lambda c, k: c.get(k, {}), modified_parameter_string_path, cfn.template):
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
                message = 'Found an embedded parameter "{}" outside of an "Fn::Sub" at {}'.format(
                    variable, '/'.join(map(str, path)))
                matches.append(RuleMatch(path, message))

        return matches
