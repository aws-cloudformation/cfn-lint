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
from cfnlint import CloudFormationLintRule
from cfnlint import RuleMatch


class Stages(CloudFormationLintRule):
    """Check if CodePipeline Stages are set up properly."""
    id = 'E2540'
    shortdesc = 'CodePipeline Stages'
    description = 'See if CodePipeline stages are set correctly'
    tags = ['base', 'properties', 'codepipeline']

    def check_first_stage(self, value, path):
        """Validate the first stage of a pipeline has source actions."""
        matches = []

        first_stage = set([a.get('ActionTypeId', {}).get('Category') for a in value[0]['Actions']])
        if 'Source' not in first_stage:
            message = 'The first stage of a pipeline must contain at least one source action.'
            matches.append(RuleMatch(path + [0], message))

        if len(first_stage) != 1:
            message = 'The first stage of a pipeline must contain only source actions.'
            matches.append(RuleMatch(path + [0], message))

        return matches

    def check_source_actions(self, value, path):
        """Validate the all of the stages."""
        matches = []
        categories = set()

        for sidx, stage in enumerate(value):
            for aidx, action in enumerate(stage['Actions']):
                categories.add(action['ActionTypeId']['Category'])
                if sidx > 0 and action['ActionTypeId']['Category'] == 'Source':
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
            if stage['Name'] in stage_names:
                message = 'All stage names within a pipeline must be unique.'
                matches.append(RuleMatch(path + [sidx, 'Name'], message))
            stage_names.add(stage['Name'])

        return matches

    def match(self, cfn):
        """Check CodePipeline stages"""
        matches = list()

        resources = cfn.get_resource_properties(['AWS::CodePipeline::Pipeline'])
        for resource in resources:
            path = resource['Path']
            properties = resource['Value']

            if len(properties['Stages']) < 2:
                message = 'A pipeline must contain at least two stages.'
                matches.append(RuleMatch(path, message))

            matches.extend(
                self.check_first_stage(properties['Stages'], path + ['Stages'])
            )
            matches.extend(
                self.check_source_actions(properties['Stages'], path + ['Stages'])
            )
            matches.extend(
                self.check_names_unique(properties['Stages'], path + ['Stages'])
            )

        return matches
