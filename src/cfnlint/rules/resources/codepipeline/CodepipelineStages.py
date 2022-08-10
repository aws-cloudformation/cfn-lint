"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class CodepipelineStages(CloudFormationLintRule):
    """Check if CodePipeline Stages are set up properly."""
    id = 'E2540'
    shortdesc = 'CodePipeline Stages'
    description = 'See if CodePipeline stages are set correctly'
    source_url = 'https://docs.aws.amazon.com/codepipeline/latest/userguide/reference-pipeline-structure.html#pipeline-requirements'
    tags = ['properties', 'codepipeline']

    def _format_error_message(self, message, scenario):
        """Format error message with scenario text"""
        if scenario:
            scenario_text = ' When ' + \
                ' and '.join(['condition "%s" is %s' % (k, v) for (k, v) in scenario.items()])
            return message + scenario_text

        return message

    def check_stage_count(self, stages, path, scenario):
        """Check that there is minimum 2 stages."""
        matches = []

        if len(stages) < 2:
            message = 'CodePipeline has {} stages. There must be at least two stages.'.format(
                len(stages))
            matches.append(RuleMatch(path, self._format_error_message(message, scenario)))

        return matches

    def check_first_stage(self, stages, path, scenario):
        """Validate the first stage of a pipeline has source actions."""
        matches = []

        if len(stages) < 1:  # pylint: disable=C1801
            self.logger.debug('Stages was empty. Should have been caught by generic linting.')
            return matches

        # pylint: disable=R1718
        first_stage = set([a.get('ActionTypeId').get('Category') for a in stages[0]['Actions']])
        if first_stage and 'Source' not in first_stage:
            message = 'The first stage of a pipeline must contain at least one source action.'
            matches.append(RuleMatch(path + [0, 'Name'],
                                     self._format_error_message(message, scenario)))

        if len(first_stage) != 1:
            message = 'The first stage of a pipeline must contain only source actions.'
            matches.append(RuleMatch(path + [0, 'Name'],
                                     self._format_error_message(message, scenario)))

        return matches

    def check_source_actions(self, stages, path, scenario):
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
                    matches.append(
                        RuleMatch(path + [sidx, 'Actions', aidx], self._format_error_message(message, scenario)))

        if not (categories - set(['Source'])):
            message = 'At least one stage in pipeline must contain an action that is not a source action.'
            matches.append(RuleMatch(path, self._format_error_message(message, scenario)))

        return matches

    def check_names_unique(self, value, path, scenario):
        """Check that stage names are unique."""
        matches = []
        stage_names = set()
        for sidx, stage in enumerate(value):
            stage_name = stage.get('Name')
            if isinstance(stage_name, str):
                if stage_name in stage_names:
                    message = 'All stage names within a pipeline must be unique. ({name})'.format(
                        name=stage_name,
                    )
                    matches.append(RuleMatch(path + [sidx, 'Name'],
                                             self._format_error_message(message, scenario)))
                stage_names.add(stage_name)
            else:
                self.logger.debug('Found non string for stage name: %s', stage_name)
        return matches

    def match(self, cfn):
        """Check CodePipeline stages"""
        matches = []

        resources = cfn.get_resource_properties(['AWS::CodePipeline::Pipeline'])
        for resource in resources:
            path = resource['Path'] + ['Stages']
            properties = resource['Value']

            s_stages = cfn.get_object_without_nested_conditions(properties.get('Stages'), path)
            for s_stage in s_stages:
                s_stage_obj = s_stage.get('Object')
                s_scenario = s_stage.get('Scenario')
                if not isinstance(s_stage_obj, list):
                    self.logger.debug(
                        'Stages not list. Should have been caught by generic linting.')
                    continue

                try:
                    matches.extend(
                        self.check_stage_count(s_stage_obj, path, s_scenario)
                    )
                    matches.extend(
                        self.check_first_stage(s_stage_obj, path, s_scenario)
                    )
                    matches.extend(
                        self.check_source_actions(s_stage_obj, path, s_scenario)
                    )
                    matches.extend(
                        self.check_names_unique(s_stage_obj, path, s_scenario)
                    )
                except AttributeError as err:
                    self.logger.debug('Got AttributeError. Should have been caught by generic linting. '
                                      'Ignoring the error here: %s', str(err))

        return matches
