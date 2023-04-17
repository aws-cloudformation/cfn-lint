from cfnlint.rules.generic_match_project_validate_rule import MatchProjectValidateRule


class RuntimeCanUseZipFile(MatchProjectValidateRule):
    id = "E2553"
    yaml = """
            Description: 'AWS::Lambda::Function: Zipfile can only be use for Runtime Nodejs*'
            ErrorMessage: 'Zipfile can only be use for Nodejs or Python Runtime'
            ResourceTypes: AWS::Lambda::Function
            Conditions:
                - Fn::REGEX_MATCH:
                    - Runtime
                    - "^((?!(nodejs|python)).)*$"
            Validations:
                - Fn::IS:
                    - Code.ZipFile
                    - NOT_DEFINED
        """

    def __init__(self):
        super().__init__(RuntimeCanUseZipFile.id, RuntimeCanUseZipFile.yaml)
