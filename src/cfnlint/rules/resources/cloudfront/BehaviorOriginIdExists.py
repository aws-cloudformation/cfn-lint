from cfnlint.rules.generic_match_project_validate_rule import MatchProjectValidateRule


class BehaviorOriginIdExists(MatchProjectValidateRule):
    id = "E2554"
    yaml = """
            Description: 'AWS::Cloudfront::Distribution: TargetOriginId should match one of the Origins.Id'
            ErrorMessage: 'TargetOriginId should match one of the Origins.Id'
            ResourceTypes: AWS::CloudFront::Distribution
            Projection: DistributionConfig.Origins.Id
            Validations:
                - Fn::IN:
                    - DistributionConfig.CacheBehaviors.TargetOriginId
                    - Fn::Projection
                - Fn::IN:
                    - DistributionConfig.DefaultCacheBehavior.TargetOriginId
                    - Fn::Projection
        """

    def __init__(self):
        super().__init__(BehaviorOriginIdExists.id, BehaviorOriginIdExists.yaml)
