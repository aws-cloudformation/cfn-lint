from cfnlint.rules.generic_match_project_validate_rule import MatchProjectValidateRule


class AlarmPeriodInSecondsAWSNamespace(MatchProjectValidateRule):
    id = "E2555"
    yaml = """
            Description: 'AWS::CloudWatch::Alarm: Period in AWS Namespace should be at least 60'
            ErrorMessage: 'Period in AWS Namespace should be 60 or multiple of 60'
            ResourceTypes: AWS::CloudWatch::Alarm
            Conditions:
                - Fn::REGEX_MATCH:
                    - Namespace
                    - "^AWS/.*$"
            Validations:
                - "Fn::>=":
                    - Period
                    - 60
                - Fn::REGEX_MATCH:
                    - Period
                    - ^.*0$
        """

    def __init__(self):
        super().__init__(
            AlarmPeriodInSecondsAWSNamespace.id, AlarmPeriodInSecondsAWSNamespace.yaml
        )


class AlarmPeriodInSecondsSmallInterval(MatchProjectValidateRule):
    id = "E2556"
    yaml = """
            Description: 'AWS::CloudWatch::Alarm: Period <= 60 can only be [10, 30, 60]'
            ErrorMessage: 'Period <= 60 can only be [10, 30, 60]'
            ResourceTypes: AWS::CloudWatch::Alarm
            Conditions:
                - Fn::REGEX_MATCH:
                    - Namespace
                    - ^((?!AWS).)*$
                - "Fn::<=":
                    - Period
                    - 60
            Validations:
                - Fn::IN:
                    - Period
                    - - 10
                      - 30
                      - 60
        """

    def __init__(self):
        super().__init__(
            AlarmPeriodInSecondsSmallInterval.id, AlarmPeriodInSecondsSmallInterval.yaml
        )
