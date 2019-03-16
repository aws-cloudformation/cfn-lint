"""
  Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.

  Permission is hereby granted, free of charge, to any person obtaining a copy of this
  software and associated documentation files (the "Software"), to deal in the Software
  without restriction, including without limitation the rights to use, copy, modify,
  merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
  permit persons to whom the Software is furnished to do so.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
  INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
  PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
  HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
  OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
  SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
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
                        args.regions, args.override_spec))
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
