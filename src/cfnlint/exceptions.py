class CfnLintError(Exception):
    """
    The base exception class for cfn-lint exceptions.
    :ivar msg: The descriptive message associated with the error.
    """

    fmt = "An unspecified error occurred"

    def __init__(self, **kwargs):
        msg = self.fmt.format(**kwargs)
        Exception.__init__(self, msg)
        self.kwargs = kwargs


class DuplicateRuleError(CfnLintError):
    """
    The data associated with a particular path could not be loaded.
    :ivar data_path: The data path that the user attempted to load.
    """

    fmt = "Rule already included: {rule_id}"
