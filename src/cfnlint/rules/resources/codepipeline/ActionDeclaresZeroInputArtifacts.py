from cfnlint import CloudFormationLintRule
from cfnlint import RuleMatch


class ActionDeclaresZeroInputArtifacts(CloudFormationLintRule):
    """Check that first stage is source only in a pipeline."""
    id = 'E9002'
    shortdesc = 'Action declares 0 input artifacts'
    description = 'Check that pipeline stage actions have input artifacts'
    tags = ['base', 'resources', 'codepipeline']

    def match(self, cfn):
        matches = list()

        resources = cfn.get_resources(['AWS::CodePipeline::Pipeline'])
        for resource_name, resource_obj in resources.items():
            resource_type = resource_obj.get('Type', '')
            resource_properties = resource_obj.get('Properties', {})
            if 'Stages' not in resource_properties:
                continue

            stages = resource_properties['Stages'][1:]
            for sid, stage in enumerate(stages):
                actions = stage['Actions']
                for aid, action in enumerate(actions):
                    if action['ActionTypeId']['Category'] != 'Build':
                        continue
                    if not action.get('InputArtifacts'):
                        message = f'Action {action["Name"]} declares 0 artifacts which is less than the minimum count(1)'
                        matches.append(RuleMatch(
                            [
                                'Resources',
                                resource_name,
                                'Properties',
                                'Stages',
                                sid,
                                'Actions',
                                aid,
                            ],
                            message,
                        ))

        return matches
