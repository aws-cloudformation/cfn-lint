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
    """Main function"""
    if sys.version_info[:2] == (3, 4):
        warnings.warn('Python 3.4 has reached end of life. '
                      'cfn-lint will end support for python 3.4 on July 1st, 2020.', Warning, stacklevel=3)
    elif sys.version_info[:2] == (2, 7):
        warnings.warn('Python 2.7 has reached end of life. '
                      'cfn-lint will end support for python 2.7 on December 31st, 2020.', Warning, stacklevel=3)

    try:
        (args, filenames, formatter) = cfnlint.core.get_args_filenames(sys.argv[1:])
        matches = []
        rules = None
        for filename in filenames:
            LOGGER.debug('Begin linting of file: %s', str(filename))
            (template, rules, errors) = cfnlint.core.get_template_rules(filename, args)
            # template matches may be empty but the template is still None
            # this happens when ignoring bad templates
            if not errors and template:
                matches.extend(
                    cfnlint.core.run_cli(
                        filename, template, rules,
                        args.regions, args.override_spec, args.build_graph, args.mandatory_checks))
            else:
                matches.extend(errors)
            LOGGER.debug('Completed linting of file: %s', str(filename))

        matches_output = formatter.print_matches(matches, rules)

        if matches_output:
            if args.output_file:
                with open(args.output_file, 'w') as output_file:
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
