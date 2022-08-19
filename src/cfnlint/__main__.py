"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import warnings
import sys
import logging
import cfnlint.core


LOGGER = logging.getLogger('cfnlint')


def main():
    if sys.version_info[:2] == (3, 4):
        warnings.warn('Python 3.4 has reached end of life. '
                      'cfn-lint has ended support for python 3.4 as of July 1st, 2020.', Warning, stacklevel=3)
    elif sys.version_info[:2] == (3, 5):
        warnings.warn('Python 3.5 has reached end of life. '
                      'cfn-lint has ended support for python 3.5 as of August 1st, 2021.', Warning, stacklevel=3)
    elif sys.version_info[:2] == (2, 7):
        warnings.warn('Python 2.7 has reached end of life. '
                      'cfn-lint will end support for python 2.7 on June 1st, 2020.', Warning, stacklevel=3)

    try:
        (args, filenames, formatter) = cfnlint.core.get_args_filenames(sys.argv[1:])
        matches = list(cfnlint.core.get_matches(filenames, args))
        rules = cfnlint.core.get_used_rules()
        matches_output = formatter.print_matches(matches, rules, filenames)

        if matches_output:
            if args.output_file:
                with open(args.output_file, 'w', encoding='utf-8') as output_file:
                    output_file.write(matches_output)
            else:
                print(matches_output)

        return cfnlint.core.get_exit_code(matches)
    except cfnlint.core.CfnLintExitException as e:
        LOGGER.error(str(e))
        return e.exit_code


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, TypeError):
        LOGGER.error(ValueError)
