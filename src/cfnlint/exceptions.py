"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations


class CfnLintExitException(Exception):
    """
    An exception that is raised to indicate that the CloudFormation linter should exit.

    This exception is used to signal that the linter should exit
    with a specific exit code, typically indicating the severity
    of the issues found in the CloudFormation template.

    Attributes:
        exit_code (int): The exit code to be used when the linter exits.

    Methods:
        __init__(self, msg: str | None=None, exit_code: int=1) -> None:
            Initialize a new CfnLintExitException instance with the specified exit code.
    """

    def __init__(self, msg: str | None = None, exit_code: int = 1):
        """
        Initialize a new CfnLintExitException instance with the specified exit code.

        Args:
            exit_code (int): The exit code to be used when the linter exits.
        """
        if msg is None:
            msg = f"process failed with exit code {exit_code}"
        super().__init__(msg)
        self.exit_code = exit_code


class InvalidRegionException(CfnLintExitException):
    """
    An exception that is raised when an invalid AWS region is encountered.

    This exception is raised when the CloudFormation linter encounters a resource
    or parameter that references an AWS region that is not valid or supported.
    """


class UnexpectedRuleException(CfnLintExitException):
    """
    An exception that is raised when an unexpected error occurs while loading rules.

    This exception is raised when the CloudFormation linter encounters an error
    while attempting to load custom rules or rules from a specified directory or
    module. This could be due to a variety of reasons, such as a missing file,
    a syntax error in the rule code, or an issue with the rule implementation.
    """


class DuplicateRuleError(CfnLintExitException):
    """
    An exception that is raised when an unexpected error occurs while loading rules.

    This exception is raised when the CloudFormation linter encounters a rule with a
    duplicate ID.
    """

    def __init__(self, rule_id: str):
        """
        Initialize a new CfnLintExitException instance with the specified exit code.

        Args:
            rule_id (str): The rule ID that a duplicate was found for.
        """
        super().__init__(f"Rule already included: {rule_id}")
