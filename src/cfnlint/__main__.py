"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import logging
import sys
import warnings

import cfnlint.core

LOGGER = logging.getLogger("cfnlint")


def main():
    try:
        (config, filenames, formatter) = cfnlint.core.get_args_filenames(sys.argv[1:])
        matches = list(cfnlint.core.get_matches(filenames, config))
        rules = cfnlint.core.get_used_rules()
        matches_output = formatter.print_matches(matches, rules, filenames)

        if matches_output:
            if config.output_file:
                with open(config.output_file, "w", encoding="utf-8") as output_file:
                    output_file.write(matches_output)
            else:
                print(matches_output)

        return cfnlint.core.get_exit_code(matches, config.non_zero_exit_code)
    except cfnlint.core.CfnLintExitException as e:
        LOGGER.error(str(e))
        return e.exit_code


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, TypeError):
        LOGGER.error(ValueError)
