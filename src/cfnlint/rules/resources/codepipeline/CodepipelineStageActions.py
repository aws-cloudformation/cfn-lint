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
import re
import six
from cfnlint import CloudFormationLintRule
from cfnlint import RuleMatch


class CodepipelineStageActions(CloudFormationLintRule):
    """Check if CodePipeline Stage Actions are set up properly."""
    id = 'E2541'
    shortdesc = 'CodePipeline Stage Actions'
    description = 'See if CodePipeline stage actions are set correctly'
    source_url = 'https://docs.aws.amazon.com/codepipeline/latest/userguide/reference-pipeline-structure.html#pipeline-requirements'
    tags = ['resources', 'codepipeline']

    CONSTRAINTS = {
        'AWS': {
            'Source': {
                'S3': {
                    'InputArtifactRange': 0,
                    'OutputArtifactRange': 1,
                },
                'CodeCommit': {
                    'InputArtifactRange': 0,
                    'OutputArtifactRange': 1,
                }
            },
            'Test': {
                'CodeBuild': {
                    'InputArtifactRange': (1, 5),
                    'OutputArtifactRange': (0, 5),
                }
            },
            'Build': {
                'CodeBuild': {
                    'InputArtifactRange': (1, 5),
                    'OutputArtifactRange': (0, 5),
                }
            },
            'Approval': {
                'Manual': {
                    'InputArtifactRange': 0,
                    'OutputArtifactRange': 0,
                }
            },
            'Deploy': {
                'CloudFormation': {
                    'InputArtifactRange': (0, 10),
                    'OutputArtifactRange': (0, 1),
                },
                'CodeDeploy': {
                    'InputArtifactRange': 1,
                    'OutputArtifactRange': 0,
                },
                'ElasticBeanstalk': {
                    'InputArtifactRange': 1,
                    'OutputArtifactRange': 0,
                },
                'OpsWorks': {
                    'InputArtifactRange': 1,
                    'OutputArtifactRange': 0,
                },
                'ECS': {
                    'InputArtifactRange': 1,
                    'OutputArtifactRange': 0,
                },
            },
            'Invoke': {
                'Lambda': {
                    'InputArtifactRange': (0, 5),
                    'OutputArtifactRange': (0, 5),
                }
            }
        },
        'ThirdParty': {
            'Source': {
                'GitHub': {
                    'InputArtifactRange': 0,
                    'OutputArtifactRange': 1,
                }
            },
        },
    }

    KEY_MAP = {
        'InputArtifacts': 'InputArtifactRange',
        'OutputArtifacts': 'OutputArtifactRange',
    }


    def check_artifact_counts(self, action, artifact_type, path):
        """Check that artifact counts are within valid ranges."""
        matches = []

        action_type_id = action.get('ActionTypeId')
        owner = action_type_id.get('Owner')
        category = action_type_id.get('Category')
        provider = action_type_id.get('Provider')

        if isinstance(owner, dict) or isinstance(category, dict) or isinstance(provider, dict):
            self.logger.debug('owner, category, provider need to be strings to validate. Skipping.')
            return matches

        constraints = self.CONSTRAINTS.get(owner, {}).get(category, {}).get(provider, {})
        if not constraints:
            return matches
        artifact_count = len(action.get(artifact_type, []))

        constraint_key = self.KEY_MAP[artifact_type]
        if isinstance(constraints[constraint_key], tuple):
            min_, max_ = constraints[constraint_key]
            if not (min_ <= artifact_count <= max_):
                message = (
                    'Action "{action}" declares {number} {artifact_type} which is not in '
                    'expected range [{a}, {b}].'
                ).format(
                    action=action['Name'],
                    number=artifact_count,
                    artifact_type=artifact_type,
                    a=min_,
                    b=max_
                )
                matches.append(RuleMatch(
                    path + [artifact_type],
                    message
                ))
        else:
            if artifact_count != constraints[constraint_key]:
                message = (
                    'Action "{action}" declares {number} {artifact_type} which is not the '
                    'expected number [{a}].'
                ).format(
                    action=action['Name'],
                    number=artifact_count,
                    artifact_type=artifact_type,
                    a=constraints[constraint_key]
                )
                matches.append(RuleMatch(
                    path + [artifact_type],
                    message
                ))

        return matches

    def check_version(self, action, path):
        """Check that action type version is valid."""
        matches = []

        REGEX_VERSION_STRING = re.compile(r'^[0-9A-Za-z_-]+$')
        LENGTH_MIN = 1
        LENGTH_MAX = 9

        version = action.get('ActionTypeId', {}).get('Version')
        if isinstance(version, dict):
            self.logger.debug('Unable to validate version when an object is used.  Skipping')
        elif isinstance(version, (six.string_types)):
            if not LENGTH_MIN <= len(version) <= LENGTH_MAX:
                message = 'Version string ({0}) must be between {1} and {2} characters in length.'
                matches.append(RuleMatch(
                    path + ['ActionTypeId', 'Version'],
                    message.format(version, LENGTH_MIN, LENGTH_MAX)))
            elif not re.match(REGEX_VERSION_STRING, version):
                message = 'Version string must match the pattern [0-9A-Za-z_-]+.'
                matches.append(RuleMatch(
                    path + ['ActionTypeId', 'Version'],
                    message
                ))
        return matches

    def check_names_unique(self, action, path, action_names):
        """Check that action names are unique."""
        matches = []

        action_name = action.get('Name')
        if isinstance(action_name, six.string_types):
            if action.get('Name') in action_names:
                message = 'All action names within a stage must be unique. ({name})'.format(
                    name=action.get('Name')
                )
                matches.append(RuleMatch(path + ['Name'], message))
            action_names.add(action.get('Name'))

        return matches

    def match(self, cfn):
        """Check that stage actions are set up properly."""
        matches = []

        resources = cfn.get_resource_properties(['AWS::CodePipeline::Pipeline'])
        for resource in resources:
            path = resource['Path']
            properties = resource['Value']

            s_stages = properties.get_safe('Stages', path)
            for s_stage_v, s_stage_p in s_stages:
                if not isinstance(s_stage_v, list):
                    self.logger.debug('Stages not list. Should have been caught by generic linting.')
                    return matches

                for l_i_stage, l_i_path in s_stage_v.items_safe(s_stage_p):
                    action_names = set()
                    s_actions = l_i_stage.get_safe('Actions', l_i_path)
                    for s_action_v, s_action_p in s_actions:
                        if not isinstance(s_action_v, list):
                            self.logger.debug('Actions not list. Should have been caught by generic linting.')
                            return matches

                        for l_i_a_action, l_i_a_path in s_action_v.items_safe(s_action_p):
                            try:
                                full_path = path + l_i_path + l_i_a_path
                                matches.extend(self.check_names_unique(l_i_a_action, full_path, action_names))
                                matches.extend(self.check_version(l_i_a_action, full_path))
                                matches.extend(self.check_artifact_counts(l_i_a_action, 'InputArtifacts', full_path))
                                matches.extend(self.check_artifact_counts(l_i_a_action, 'OutputArtifacts', full_path))
                            except AttributeError as err:
                                self.logger.debug('Got AttributeError. Should have been caught by generic linting. '
                                                  'Ignoring the error here: %s', str(err))

        return matches
