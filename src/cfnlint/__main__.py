"""
Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import sys
import logging
import cfnlint.core


LOGGER = logging.getLogger('cfnlint')


def main():
    """Main function"""
    try:
        (args, filenames, formatter) = cfnlint.core.get_args_filenames(sys.argv[1:])
        matches = []
        for filename in filenames:
            LOGGER.debug('Begin linting of file: %s', str(filename))
            (template, rules, template_matches) = cfnlint.core.get_template_rules(filename, args)
            if not template_matches:
                matches.extend(
                    cfnlint.core.run_cli(
                        filename, template, rules,
                        args.regions, args.override_spec, args.mandatory_checks))
            else:
                matches.extend(template_matches)
            LOGGER.debug('Completed linting of file: %s', str(filename))

        matches_output = formatter.print_matches(matches)
        if matches_output:
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
