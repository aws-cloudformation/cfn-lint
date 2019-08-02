"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import sys
import logging
import cfnlint
import cfnlint.formatters


LOGGER = logging.getLogger('cfnlint')


def main():
    """Main function"""
    try:
        linter = cfnlint.CliLinter(sys.argv[1:])
        return linter.run_cli()
    except cfnlint.CfnLintExitException as e:
        LOGGER.error(str(e))
        return e.exit_code


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, TypeError):
        LOGGER.error(ValueError)
