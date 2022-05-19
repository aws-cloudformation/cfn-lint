"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import json
from cfnlint.rules import CloudFormationLintRule
from cfnlint.rules import RuleMatch


class StateMachine(CloudFormationLintRule):
    """Check State Machine Definition"""
    id = 'E2532'
    shortdesc = 'Check State Machine Definition for proper syntax'
    description = 'Check the State Machine String Definition to make sure its JSON. ' \
        'Validate basic syntax of the file to determine validity.'
    source_url = 'https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-stepfunctions-statemachine.html'
    tags = ['resources', 'stepfunctions']

    def __init__(self):
        """Init"""
        super(StateMachine, self).__init__()
        self.resource_property_types.append('AWS::StepFunctions::StateMachine')

    def _check_state_json(self, def_json, state_name, path):
        """Check State JSON Definition"""
        matches = []

        # https://docs.aws.amazon.com/step-functions/latest/dg/amazon-states-language-common-fields.html
        common_state_keys = [
            'Next',
            'End',
            'Type',
            'Comment',
            'InputPath',
            'OutputPath',
        ]
        common_state_required_keys = [
            'Type',
        ]
        state_key_types = {
            'Pass': ['Result', 'ResultPath', 'Parameters'],
            'Task': ['Resource', 'ResultPath', 'ResultSelector', 'Retry', 'Catch',
                     'TimeoutSeconds', 'Parameters', 'HeartbeatSeconds'],
            'Map': ['MaxConcurrency', 'Iterator', 'ItemsPath', 'ResultPath',
                    'ResultSelector', 'Retry', 'Catch', 'Parameters'],
            'Choice': ['Choices', 'Default'],
            'Wait': ['Seconds', 'Timestamp', 'SecondsPath', 'TimestampPath'],
            'Succeed': [],
            'Fail': ['Cause', 'Error'],
            'Parallel': ['Branches', 'ResultPath', 'ResultSelector', 'Parameters', 'Retry', 'Catch']
        }
        state_required_types = {
            'Pass': [],
            'Task': ['Resource'],
            'Choice': ['Choices'],
            'Wait': [],
            'Succeed': [],
            'Fail': [],
            'Parallel': ['Branches']
        }

        for req_key in common_state_required_keys:
            if req_key not in def_json:
                message = 'State Machine Definition required key (%s) for State (%s) is missing' % (
                    req_key, state_name)
                matches.append(RuleMatch(path, message))
                return matches

        state_type = def_json.get('Type')

        if state_type in state_key_types:
            for state_key, _ in def_json.items():
                if state_key not in common_state_keys + state_key_types.get(state_type, []):
                    message = 'State Machine Definition key (%s) for State (%s) of Type (%s) is not valid' % (
                        state_key, state_name, state_type)
                    matches.append(RuleMatch(path, message))
            for req_key in common_state_required_keys + state_required_types.get(state_type, []):
                if req_key not in def_json:
                    message = 'State Machine Definition required key (%s) for State (%s) of Type (%s) is missing' % (
                        req_key, state_name, state_type)
                    matches.append(RuleMatch(path, message))
                    return matches
        else:
            message = 'State Machine Definition Type (%s) is not valid' % (state_type)
            matches.append(RuleMatch(path, message))

        return matches

    def _check_definition_json(self, def_json, path):
        """Check JSON Definition"""
        matches = []

        top_level_keys = [
            'Comment',
            'StartAt',
            'TimeoutSeconds',
            'Version',
            'States'
        ]
        top_level_required_keys = [
            'StartAt',
            'States'
        ]
        for top_key, _ in def_json.items():
            if top_key not in top_level_keys:
                message = 'State Machine Definition key (%s) is not valid' % top_key
                matches.append(RuleMatch(path, message))

        for req_key in top_level_required_keys:
            if req_key not in def_json:
                message = 'State Machine Definition required key (%s) is missing' % req_key
                matches.append(RuleMatch(path, message))

        for state_name, state_value in def_json.get('States', {}).items():
            matches.extend(self._check_state_json(state_value, state_name, path))
        return matches

    def check_value(self, value, path, fail_on_loads=True):
        """Check Definition Value"""
        matches = []
        try:
            def_json = json.loads(value)
        # pylint: disable=W0703
        except Exception as err:
            if fail_on_loads:
                message = 'State Machine Definition needs to be formatted as JSON. Error %s' % err
                matches.append(RuleMatch(path, message))
                return matches

            self.logger.debug('State Machine definition could not be parsed. Skipping')
            return matches

        matches.extend(self._check_definition_json(def_json, path))
        return matches

    def check_sub(self, value, path):
        """Check Sub Object"""
        matches = []
        if isinstance(value, list):
            matches.extend(self.check_value(value[0], path, False))
        elif isinstance(value, str):
            matches.extend(self.check_value(value, path, False))

        return matches

    def match_resource_properties(self, properties, _, path, cfn):
        """Check CloudFormation Properties"""
        matches = []

        matches.extend(
            cfn.check_value(
                obj=properties, key='DefinitionString',
                path=path[:],
                check_value=self.check_value,
                check_sub=self.check_sub
            ))

        return matches
