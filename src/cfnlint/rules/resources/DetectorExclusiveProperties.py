from cfnlint.rules import CloudFormationLintRule, RuleMatch

class DetectorExclusiveProperties(CloudFormationLintRule):
    id = "E3063"
    shortdesc = "Validate GuardDuty Detector property exclusivity"
    description = "Check that DataSources and Features are not used together."
    source_url = "https://docs.aws.amazon.com/pt_br/guardduty/latest/ug/guardduty-features-activation-model.html"
    tags = ["resources", "guardduty"]

    def match(self, cfn):
        matches = []
        resources = cfn.get_resources(['AWS::GuardDuty::Detector'])
        
        for resource_name, resource in resources.items():
            properties = resource.get('Properties', {})
            if 'DataSources' in properties and 'Features' in properties:
                path = ['Resources', resource_name, 'Properties']
                message = "Both 'DataSources' and 'Features' provided at {0}. Use 'Features' instead."
                matches.append(RuleMatch(path, message.format(resource_name)))
        
        return matches