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
import json
import six
from cfnlint import CloudFormationLintRule
from cfnlint import RuleMatch


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
        self.resource_property_types.append('AWS::StepFunctions::StateMachine')

    def _check_state_json(self, def_json, state_name, path):
        """Check State JSON Definition"""
        matches = []

        common_state_keys = [
            'Next',
            'End',
            'Type',
            'Comment',
            'Input',
            'Ouptut',
        ]
        common_state_required_keys = [
            'Type',
        ]
        state_key_types = {
            'Pass': ['Result', 'ResultPath'],
            'Task': ['Resource', 'ResultPath', 'Retry', 'Catch', 'TimeoutSeconds', 'HeartbeatSeconds'],
            'Choice': ['Choices', 'Default'],
            'Wait': ['Seconds', 'Timestamp', 'SecondsPath', 'TimestampPath'],
            'Succeed': [],
            'Fail': ['Cause', 'Error'],
            'Parallel': ['Branches', 'ResultPath', 'Retry', 'Catch']
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
                message = 'State Machine Definition required key (%s) for State (%s) is missing' % (req_key, state_name)
                matches.append(RuleMatch(path, message))
                return matches

        state_type = def_json.get('Type')

        if state_type in state_key_types:
            for state_key, _ in def_json.items():
                if state_key not in common_state_keys + state_key_types.get(state_type, []):
                    message = 'State Machine Definition key (%s) for State (%s) of Type (%s) is not valid' % (state_key, state_name, state_type)
                    matches.append(RuleMatch(path, message))
            for req_key in common_state_required_keys + state_required_types.get(state_type, []):
                if req_key not in def_json:
                    message = 'State Machine Definition required key (%s) for State (%s) of Type (%s) is missing' % (req_key, state_name, state_type)
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

    def check_value(self, value, path):
        """Check Definition Value"""
        matches = []
        try:
            def_json = json.loads(value)
        # pylint: disable=W0703
        except Exception as err:
            message = 'State Machine Definition needs to be formatted as JSON. Error %s' % err
            matches.append(RuleMatch(path, message))
            return matches

        matches.extend(self._check_definition_json(def_json, path))
        return matches

    def check_sub(self, value, path):
        """Check Sub Object"""
        matches = []
        if isinstance(value, list):
            matches.extend(self.check_value(value[0], path))
        elif isinstance(value, six.string_types):
            matches.extend(self.check_value(value, path))

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
