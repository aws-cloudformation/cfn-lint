"""
  Copyright 2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.

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
import logging
import os
from cfnlint import RulesCollection
from cfnlint.config import ConfigMixIn
import cfnlint.formatters
import cfnlint.decode
import cfnlint.maintenance
from cfnlint.version import __version__
from cfnlint.helpers import REGIONS


LOGGER = logging.getLogger('cfnlint')
DEFAULT_RULESDIR = os.path.join(os.path.dirname(__file__), 'rules')


def run_cli(filename, template, rules, regions, override_spec):
    """Process args and run"""

    if override_spec:
        cfnlint.helpers.override_specs(override_spec)

    return run_checks(filename, template, rules, regions)


def get_exit_code(matches):
    """ Determine exit code """
    exit_code = 0
    for match in matches:
        if match.rule.id[0] == 'I':
            exit_code = exit_code | 8
        elif match.rule.id[0] == 'W':
            exit_code = exit_code | 4
        elif match.rule.id[0] == 'E':
            exit_code = exit_code | 2

    return exit_code


def configure_logging(debug_logging):
    """Setup Logging"""
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    if debug_logging:
        LOGGER.setLevel(logging.DEBUG)
    else:
        LOGGER.setLevel(logging.INFO)
    log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(log_formatter)

    # make sure all other log handlers are removed before adding it back
    for handler in LOGGER.handlers:
        LOGGER.removeHandler(handler)
    LOGGER.addHandler(ch)


def get_formatter(fmt):
    """ Get Formatter"""
    formatter = {}
    if fmt:
        if fmt == 'quiet':
            formatter = cfnlint.formatters.QuietFormatter()
        elif fmt == 'parseable':
            # pylint: disable=bad-option-value
            formatter = cfnlint.formatters.ParseableFormatter()
        elif fmt == 'json':
            formatter = cfnlint.formatters.JsonFormatter()
    else:
        formatter = cfnlint.formatters.Formatter()

    return formatter


def get_rules(rulesdir, ignore_rules, include_rules):
    """Get rules"""
    rules = RulesCollection(ignore_rules, include_rules)
    rules_dirs = [DEFAULT_RULESDIR] + rulesdir
    try:
        for rules_dir in rules_dirs:
            rules.extend(
                RulesCollection.create_from_directory(rules_dir))
    except OSError as e:
        LOGGER.error('Tried to append rules but got an error: %s', str(e))
        exit(1)

    return rules


def get_args_filenames(cli_args):
    """ Get Template Configuration items and set them as default values"""

    config = ConfigMixIn(cli_args)

    configure_logging(config.debug)

    fmt = config.format
    formatter = get_formatter(fmt)

    rules = cfnlint.core.get_rules(config.append_rules, config.ignore_checks, config.include_checks)

    if config.update_specs:
        cfnlint.maintenance.update_resource_specs()
        exit(0)

    if config.update_documentation:
        cfnlint.maintenance.update_documentation(rules)
        exit(0)

    if config.listrules:
        print(rules)
        exit(0)

    if not config.templates:
        # Not specified, print the help
        config.parser.print_help()
        exit(1)

    return(config, config.templates, formatter)


def get_template_rules(filename, args):
    """ Get Template Configuration items and set them as default values"""

    (template, matches) = cfnlint.decode.decode(filename, args.ignore_bad_template)

    if matches:
        return(template, [], matches)

    args.template_args = template

    rules = cfnlint.core.get_rules(args.append_rules, args.ignore_checks, args.include_checks)

    return(template, rules, [])


def run_checks(filename, template, rules, regions):
    """Run Checks against the template"""
    if regions:

        for region in regions:
            if region not in REGIONS:
                LOGGER.error('Supported regions are %s', REGIONS)
                exit(32)

    matches = []

    runner = cfnlint.Runner(rules, filename, template, regions)
    matches.extend(runner.transform())
    # Only do rule analysis if Transform was successful
    if not matches:
        try:
            matches.extend(runner.run())
        except Exception as err:  # pylint: disable=W0703
            LOGGER.error('Tried to process rules on file %s but got an error: %s', filename, str(err))
            exit(1)
    matches.sort(key=lambda x: (x.filename, x.linenumber, x.rule.id))

    return(matches)
