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
import six
from cfnlint import CloudFormationLintRule
from cfnlint import RuleMatch


class CodepipelineStages(CloudFormationLintRule):
    """Check if CodePipeline Stages are set up properly."""
    id = 'E2540'
    shortdesc = 'CodePipeline Stages'
    description = 'See if CodePipeline stages are set correctly'
    source_url = 'https://docs.aws.amazon.com/codepipeline/latest/userguide/reference-pipeline-structure.html#pipeline-requirements'
    tags = ['properties', 'codepipeline']

    def check_stage_count(self, stages, path):
        """Check that there is minimum 2 stages."""
        matches = []

        if len(stages) < 2:
            message = 'A pipeline must contain at least two stages.'
            matches.append(RuleMatch(path, message))

        return matches

    def check_first_stage(self, stages, path):
        """Validate the first stage of a pipeline has source actions."""
        matches = []

        if len(stages) < 1:  # pylint: disable=C1801
            self.logger.debug('Stages was empty. Should have been caught by generic linting.')
            return matches

        # pylint: disable=R1718
        first_stage = set([a.get('ActionTypeId').get('Category') for a in stages[0]['Actions']])
        if first_stage and 'Source' not in first_stage:
            message = 'The first stage of a pipeline must contain at least one source action.'
            matches.append(RuleMatch(path + [0], message))

        if len(first_stage) != 1:
            message = 'The first stage of a pipeline must contain only source actions.'
            matches.append(RuleMatch(path + [0], message))

        return matches

    def check_source_actions(self, stages, path):
        """Validate the all of the stages."""
        matches = []
        categories = set()

        if len(stages) < 1:  # pylint: disable=C1801
            self.logger.debug('Stages was empty. Should have been caught by generic linting.')
            return matches

        for sidx, stage in enumerate(stages):
            for aidx, action in enumerate(stage.get('Actions', [])):
                action_type_id = action.get('ActionTypeId')
                categories.add(action_type_id.get('Category'))
                if sidx > 0 and action_type_id.get('Category') == 'Source':
                    message = 'Only the first stage of a pipeline may contain source actions.'
                    matches.append(RuleMatch(path + [sidx, 'Actions', aidx], message))

        if not (categories - set(['Source'])):
            message = 'At least one stage in pipeline must contain an action that is not a source action.'
            matches.append(RuleMatch(path, message))

        return matches

    def check_names_unique(self, value, path):
        """Check that stage names are unique."""
        matches = []
        stage_names = set()
        for sidx, stage in enumerate(value):
            stage_name = stage.get('Name')
            if isinstance(stage_name, six.string_types):
                if stage_name in stage_names:
                    message = 'All stage names within a pipeline must be unique. ({name})'.format(
                        name=stage_name,
                    )
                    matches.append(RuleMatch(path + [sidx, 'Name'], message))
                stage_names.add(stage_name)
            else:
                self.logger.debug('Found non string for stage name: %s', stage_name)
        return matches

    def match(self, cfn):
        """Check CodePipeline stages"""
        matches = []

        resources = cfn.get_resource_properties(['AWS::CodePipeline::Pipeline'])
        for resource in resources:
            path = resource['Path']
            properties = resource['Value']

            stages = properties.get('Stages')
            if not isinstance(stages, list):
                self.logger.debug('Stages not list. Should have been caught by generic linting.')
                return matches

            try:
                matches.extend(
                    self.check_stage_count(stages, path + ['Stages'])
                )
                matches.extend(
                    self.check_first_stage(stages, path + ['Stages'])
                )
                matches.extend(
                    self.check_source_actions(stages, path + ['Stages'])
                )
                matches.extend(
                    self.check_names_unique(stages, path + ['Stages'])
                )
            except AttributeError as err:
                self.logger.debug('Got AttributeError. Should have been caught by generic linting. '
                                  'Ignoring the error here: %s', str(err))


        return matches
