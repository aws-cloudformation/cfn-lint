from cfnlint import CloudFormationLintRule
from cfnlint import RuleMatch


class PipelineShouldStartWithSourceStage(CloudFormationLintRule):
    """Check that first stage is source only in a pipeline."""
    id = 'E9001'
    shortdesc = 'Pipeline should start with a stage that only contains source actions.'
    description = 'Check that first stage in pipeline has source actions only.'
    tags = ['base', 'resources', 'codepipeline']

    def match(self, cfn):
        matches = list()

        resources = cfn.get_resources(['AWS::CodePipeline::Pipeline'])
        for resource_name, resource_obj in resources.items():
            resource_type = resource_obj.get('Type', '')
            resource_properties = resource_obj.get('Properties', {})
            if 'Stages' not in resource_properties:
                continue

            actions = resource_properties['Stages'][0]['Actions']
            action_type_ids = {a['ActionTypeId']['Category'] for a in actions}
            if 'Source' not in action_type_ids:
                continue
            if len(action_type_ids) == 1:
                continue

            for idx, action in enumerate(actions):
                category = action['ActionTypeId']['Category']
                if category != 'Source':
                    message = f'Pipeline has {category} category action when it should only have source.'
                    matches.append(RuleMatch(
                        [
                            'Resources',
                            resource_name,
                            'Properties',
                            'Stages',
                            0,
                            'Actions',
                            idx,
                            'ActionTypeId',
                            'Category'
                        ],
                        message
                    ))

        return matches
