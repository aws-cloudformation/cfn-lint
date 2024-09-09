"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import argparse
import copy
import glob
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, Sequence, TypedDict

from typing_extensions import Unpack

import cfnlint.decode.cfn_yaml
from cfnlint.helpers import REGIONS, format_json_string
from cfnlint.jsonschema import StandardValidator
from cfnlint.version import __version__

# pylint: disable=too-many-public-methods
LOGGER = logging.getLogger("cfnlint")

_DEFAULT_RULESDIR = os.path.join(os.path.dirname(__file__), "rules")


def configure_logging(debug_logging, info_logging):
    ch = logging.StreamHandler()

    if debug_logging:
        LOGGER.setLevel(logging.DEBUG)
    elif info_logging:
        LOGGER.setLevel(logging.INFO)
    else:
        LOGGER.setLevel(logging.WARNING)
    log_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    ch.setFormatter(log_formatter)

    # make sure all other log handlers are removed before adding it back
    for handler in LOGGER.handlers:
        LOGGER.removeHandler(handler)
    LOGGER.addHandler(ch)


class ConfigFileArgs:
    """
    Config File arguments.
    Parses .cfnlintrc OR .cfnlintrc.yaml OR .cfnlintrc.yml
    in the Home and Project folder.
    """

    file_args: Dict = {}
    _user_config_file = None
    _project_config_file = None
    _custom_config_file = None

    def __init__(self, schema=None, config_file=None):
        # self.file_args = self.get_config_file_defaults()
        self.file_args = {}
        self.default_schema_file = Path(__file__).parent.joinpath(
            "data/CfnLintCli/config/schema.json"
        )
        with self.default_schema_file.open(encoding="utf-8") as f:
            self.default_schema = json.load(f)
        self.schema = self.default_schema if not schema else schema

        if config_file:
            self._custom_config_file = config_file
        else:
            LOGGER.debug("Looking for CFLINTRC before attempting to load")
            self._user_config_file, self._project_config_file = self._find_config()

        self.load()

    def _find_config(self):
        """Looks up for user and project level config
        Returns
        -------
        Tuple
            (Path, Path)
            Tuple with both configs and whether they were found
        Example
        -------
            > user_config, project_config = self._find_config()
        """
        config_file_name = ".cfnlintrc"

        user_config_path = ""
        home_path = Path.home()
        for path in [
            home_path.joinpath(config_file_name),
            home_path.joinpath(f"{config_file_name}.yaml"),
            home_path.joinpath(f"{config_file_name}.yml"),
        ]:
            if self._has_file(path):
                user_config_path = path
                break

        project_config_path = ""
        cwd_path = Path.cwd()
        for path in [
            cwd_path.joinpath(config_file_name),
            cwd_path.joinpath(f"{config_file_name}.yaml"),
            cwd_path.joinpath(f"{config_file_name}.yml"),
        ]:
            if self._has_file(path):
                project_config_path = path
                break

        return user_config_path, project_config_path

    def _has_file(self, filename):
        """Confirm whether file exists
        Parameters
        ----------
        filename : str
            Path to a file
        Returns
        -------
        Boolean
        """

        return Path(filename).is_file()

    def load(self):
        """Load configuration file and expose as a dictionary
        Returns
        -------
        Dict
            CFLINTRC configuration
        """

        if self._custom_config_file:
            custom_config = self._read_config(self._custom_config_file)
            LOGGER.debug("Validating Custom CFNLINTRC")
            self.validate_config(custom_config, self.schema)
            LOGGER.debug("Custom configuration loaded as")
            LOGGER.debug("%s", custom_config)

            self.file_args = custom_config
        else:
            user_config = self._read_config(self._user_config_file)
            LOGGER.debug("Validating User CFNLINTRC")
            self.validate_config(user_config, self.schema)

            project_config = self._read_config(self._project_config_file)
            LOGGER.debug("Validating Project CFNLINTRC")
            self.validate_config(project_config, self.schema)

            LOGGER.debug("User configuration loaded as")
            LOGGER.debug("%s", user_config)
            LOGGER.debug("Project configuration loaded as")
            LOGGER.debug("%s", project_config)

            LOGGER.debug("Merging configurations...")
            self.file_args = self.merge_config(user_config, project_config)

    def validate_config(self, config, schema):
        """Validate configuration against schema
        Parameters
        ----------
        config : dict
            CFNLINTRC configuration
        schema : dict
            JSONSchema to validate against
        Raises
        -------
        jsonschema.exceptions.ValidationError
            Returned when cfnlintrc doesn't match schema provided
        """
        LOGGER.debug("Validating CFNLINTRC config with given JSONSchema")
        LOGGER.debug("Schema used: %s", schema)
        LOGGER.debug("Config used: %s", config)

        validator = StandardValidator(schema=schema)
        validator.validate(config)
        LOGGER.debug("CFNLINTRC looks valid!")

    def merge_config(self, user_config, project_config):
        """Merge project and user configuration into a single dictionary
        Creates a new configuration with both configuration merged
        it favours project level over user configuration if keys are duplicated
        NOTE
        ----
            It takes any number of nested dicts
            It overrides lists found in user_config with project_config
        Parameters
        ----------
        user_config : Dict
            User configuration (~/.cfnlintrc) found at user's home directory
        project_config : Dict
            Project configuration (.cfnlintrc) found at current directory
        Returns
        -------
        Dict
            Merged configuration
        """
        # Recursively override User config with Project config
        for key in user_config:
            if key in project_config:
                # If both keys are the same, let's check whether they have nested keys
                if isinstance(user_config[key], dict) and isinstance(
                    project_config[key], dict
                ):
                    self.merge_config(user_config[key], project_config[key])
                else:
                    user_config[key] = project_config[key]
                    LOGGER.debug(
                        "Overriding User's key %s with Project's specific value %s.",
                        key,
                        project_config[key],
                    )

        # Project may have unique config we need to copy over too
        # so that we can have user+project config available as one
        for key in project_config:
            if key not in user_config:
                user_config[key] = project_config[key]

        return user_config

    def _read_config(self, config):
        """Parse given YAML configuration
        Returns
        -------
        Dict
            Parsed YAML configuration as dictionary
        """
        config = Path(config)
        config_template = None

        if self._has_file(config):
            LOGGER.debug("Parsing CFNLINTRC")
            config_template = cfnlint.decode.cfn_yaml.load(str(config))

        if not config_template:
            config_template = {}

        return config_template


def comma_separated_arg(string):
    """Split a comma separated string"""
    return string.split(",")


def _ensure_value(namespace, name, value):
    if getattr(namespace, name, None) is None:
        setattr(namespace, name, value)
    return getattr(namespace, name)


class RuleConfigurationAction(argparse.Action):
    """Override the default Action"""

    def __init__(
        self,
        option_strings,
        dest,
        nargs=None,
        const=None,
        default=None,
        type=None,
        choices=None,
        required=False,
        help=None,
        metavar=None,
    ):  # pylint: disable=W0622
        super().__init__(
            option_strings=option_strings,
            dest=dest,
            nargs=nargs,
            const=const,
            default=default,
            type=type,
            choices=choices,
            required=required,
            help=help,
            metavar=metavar,
        )

    def _parse_rule_configuration(self, string):
        """Parse the config rule structure"""
        configs = comma_separated_arg(string)
        results = {}
        for config in configs:
            rule_id = config.split(":")[0]
            config_name = config.split(":")[1].split("=")[0]
            config_value = config.split(":")[1].split("=")[1]
            if rule_id not in results:
                results[rule_id] = {}
            results[rule_id][config_name] = config_value

        return results

    def __call__(self, parser, namespace, values, option_string=None):
        items = copy.copy(_ensure_value(namespace, self.dest, {}))
        try:
            for value in values:
                new_value = self._parse_rule_configuration(value)
                for v_k, v_vs in new_value.items():
                    if v_k in items:
                        for s_k, s_v in v_vs.items():
                            items[v_k][s_k] = s_v
                    else:
                        items[v_k] = v_vs
            setattr(namespace, self.dest, items)
        except Exception:  # pylint: disable=W0703
            parser.print_help()
            parser.exit()


class CliArgs:
    """Base Args class"""

    def __init__(self, cli_args: Sequence[str] | None):
        self.parser = self.create_parser()
        self.cli_args = self.parser.parse_args(cli_args or [])

    def create_parser(self):
        """Do first round of parsing parameters to set options"""

        class ArgumentParser(argparse.ArgumentParser):
            """Override Argument Parser so we can control the exit code"""

            def error(self, message):
                self.print_help(sys.stderr)
                self.exit(32, f"{self.prog}: error: {message}\n")

        class ExtendAction(argparse.Action):
            """Support argument types that are lists and can
            be specified multiple times.
            """

            def __call__(self, parser, namespace, values, option_string=None):
                items = getattr(namespace, self.dest)
                items = [] if items is None else items
                for value in values:
                    if isinstance(value, list):
                        items.extend(value)
                    else:
                        items.append(value)
                setattr(namespace, self.dest, items)

        usage = (
            "\nBasic: cfn-lint test.yaml\n"
            "Ignore a rule: cfn-lint -i E3012 -- test.yaml\n"
            "Configure a rule: cfn-lint -x E3012:strict=true -t test.yaml\n"
            "Lint all yaml files in a folder: cfn-lint dir/**/*.yaml"
        )

        parser = ArgumentParser(description="CloudFormation Linter", usage=usage)
        parser.register("action", "extend", ExtendAction)

        standard = parser.add_argument_group("Standard")
        advanced = parser.add_argument_group("Advanced / Debugging")

        # Allow the template to be passes as an optional or a positional argument
        standard.add_argument(
            "templates",
            metavar="TEMPLATE",
            nargs="*",
            help="The CloudFormation template to be linted",
        )
        standard.add_argument(
            "-t",
            "--template",
            metavar="TEMPLATE",
            dest="template_alt",
            help="The CloudFormation template to be linted",
            nargs="+",
            default=[],
            action="extend",
        )
        standard.add_argument(
            "-b",
            "--ignore-bad-template",
            help="Ignore failures with Bad template",
            action="store_true",
        )
        standard.add_argument(
            "--ignore-templates",
            dest="ignore_templates",
            help="Ignore templates",
            nargs="+",
            default=[],
            action="extend",
        )
        advanced.add_argument(
            "-D", "--debug", help="Enable debug logging", action="store_true"
        )
        advanced.add_argument(
            "-I", "--info", help="Enable information logging", action="store_true"
        )
        standard.add_argument(
            "-f",
            "--format",
            help="Output Format",
            choices=["quiet", "parseable", "json", "junit", "pretty", "sarif"],
        )
        standard.add_argument(
            "-l",
            "--list-rules",
            dest="listrules",
            default=False,
            action="store_true",
            help="list all the rules",
        )
        standard.add_argument(
            "-r",
            "--regions",
            dest="regions",
            nargs="+",
            default=[],
            type=comma_separated_arg,
            action="extend",
            help="list the regions to validate against.",
        )
        advanced.add_argument(
            "-a",
            "--append-rules",
            dest="append_rules",
            nargs="+",
            default=[],
            type=comma_separated_arg,
            action="extend",
            help=(
                "specify one or more rules directories using "
                "one or more --append-rules arguments. "
            ),
        )
        standard.add_argument(
            "-i",
            "--ignore-checks",
            dest="ignore_checks",
            nargs="+",
            default=[],
            type=comma_separated_arg,
            action="extend",
            help="only check rules whose id do not match these values",
        )
        standard.add_argument(
            "-c",
            "--include-checks",
            dest="include_checks",
            nargs="+",
            default=[],
            type=comma_separated_arg,
            action="extend",
            help="include rules whose id match these values",
        )
        standard.add_argument(
            "-m",
            "--mandatory-checks",
            dest="mandatory_checks",
            nargs="+",
            default=[],
            type=comma_separated_arg,
            action="extend",
            help=(
                "always check rules whose id match these values, regardless of template"
                " exclusions"
            ),
        )
        standard.add_argument(
            "-e",
            "--include-experimental",
            help="Include experimental rules",
            action="store_true",
        )
        standard.add_argument(
            "-x",
            "--configure-rule",
            dest="configure_rules",
            nargs="+",
            default={},
            action=RuleConfigurationAction,
            help=(
                "Provide configuration for a rule. Format RuleId:key=value. Example:"
                " E3012:strict=true"
            ),
        )
        standard.add_argument(
            "--config-file",
            dest="config_file",
            help="Specify the cfnlintrc file to use",
        )
        standard.add_argument(
            "-z",
            "--custom-rules",
            dest="custom_rules",
            help="Allows specification of a custom rule file.",
        )
        advanced.add_argument(
            "-o",
            "--override-spec",
            dest="override_spec",
            help="A CloudFormation Spec override file that allows customization",
        )
        advanced.add_argument(
            "-g",
            "--build-graph",
            help=(
                "Creates a file in the same directory as the template that models the"
                " template's resources in DOT format"
            ),
            action="store_true",
        )
        advanced.add_argument(
            "-s",
            "--registry-schemas",
            help="one or more directories of CloudFormation Registry Schemas",
            action="extend",
            type=comma_separated_arg,
            nargs="+",
        )
        standard.add_argument(
            "-v",
            "--version",
            help="Version of cfn-lint",
            action="version",
            version=f"%(prog)s {__version__}",
        )
        advanced.add_argument(
            "-u",
            "--update-specs",
            help="Update the CloudFormation Specs",
            action="store_true",
        )
        advanced.add_argument(
            "-p",
            "--patch-specs",
            help="Patch the CloudFormation Specs in place",
            action="store_true",
        )
        advanced.add_argument(
            "--update-documentation", help=argparse.SUPPRESS, action="store_true"
        )
        advanced.add_argument(
            "--update-iam-policies", help=argparse.SUPPRESS, action="store_true"
        )
        standard.add_argument(
            "--output-file",
            type=str,
            default=None,
            help="Writes the output to the specified file, ideal for producing reports",
        )
        standard.add_argument(
            "--merge-configs",
            default=False,
            action="store_true",
            help="Merges lists between configuration layers",
        )
        standard.add_argument(
            "--non-zero-exit-code",
            type=str,
            default="informational",
            choices=["informational", "warning", "error", "none"],
            help="Exit code will be non zero from the specified rule class and higher",
        )
        advanced.add_argument("--force", help=argparse.SUPPRESS, action="store_true")

        return parser


class TemplateArgs:
    """Per Template Args"""

    def __init__(self, template_args):
        self.set_template_args(template_args)

    def get_template_args(self):
        return self._template_args

    def set_template_args(self, template):
        defaults = {}
        if isinstance(template, dict):
            configs = template.get("Metadata", {}).get("cfn-lint", {}).get("config", {})

            if isinstance(configs, dict):
                for key, value in {
                    "ignore_checks": (list),
                    "regions": (list),
                    "append_rules": (list),
                    "override_spec": (str),
                    "custom_rules": (str),
                    "ignore_bad_template": (bool),
                    "include_checks": (list),
                    "configure_rules": (dict),
                    "include_experimental": (bool),
                }.items():
                    if key in configs:
                        if isinstance(configs[key], value):
                            defaults[key] = configs[key]

        self._template_args = defaults

    template_args = property(get_template_args, set_template_args)


class ManualArgs(TypedDict, total=False):
    configure_rules: dict[str, dict[str, Any]]
    include_checks: list[str]
    ignore_checks: list[str]
    mandatory_checks: list[str]
    include_experimental: bool
    ignore_bad_template: bool
    ignore_templates: list
    merge_configs: bool
    non_zero_exit_code: str
    output_file: str
    regions: list


# pylint: disable=too-many-public-methods
class ConfigMixIn(TemplateArgs, CliArgs, ConfigFileArgs):
    """Mixin for the Configs"""

    def __init__(self, cli_args: list[str] | None = None, **kwargs: Unpack[ManualArgs]):
        self._manual_args = kwargs or ManualArgs()
        self._templates_to_process = False
        CliArgs.__init__(self, cli_args)
        # configure debug as soon as we can
        TemplateArgs.__init__(self, {})
        ConfigFileArgs.__init__(
            self, config_file=self._get_argument_value("config_file", False, False)
        )

    def __repr__(self):
        return format_json_string(
            {
                "ignore_checks": self.ignore_checks,
                "include_checks": self.include_checks,
                "mandatory_checks": self.mandatory_checks,
                "include_experimental": self.include_experimental,
                "configure_rules": self.configure_rules,
                "regions": self.regions,
                "ignore_bad_template": self.ignore_bad_template,
                "debug": self.debug,
                "info": self.info,
                "format": self.format,
                "templates": self.templates,
                "append_rules": self.append_rules,
                "override_spec": self.override_spec,
                "custom_rules": self.custom_rules,
                "config_file": self.config_file,
                "merge_configs": self.merge_configs,
                "non_zero_exit_code": self.non_zero_exit_code,
            }
        )

    def _get_argument_value(self, arg_name, is_template, is_config_file):
        cli_value = getattr(self.cli_args, arg_name)
        template_value = self.template_args.get(arg_name)
        file_value = self.file_args.get(arg_name)

        # merge list configurations
        # make sure we don't do an infinite loop so skip this check for merge_configs
        if arg_name != "merge_configs":
            if self.merge_configs:
                # the CLI will always have an empty list when the item is a list
                # we will use that to evaluate if we need to merge the lists
                if isinstance(cli_value, list):
                    # Use a copy here, otherwise we will
                    # accumulate template level config
                    # into the cli_value which will persist between template files
                    result = cli_value.copy()
                    if isinstance(template_value, list):
                        result.extend(template_value)
                    if isinstance(file_value, list):
                        result.extend(file_value)
                    return result

        # return individual items
        if arg_name in self._manual_args:
            return self._manual_args[arg_name]
        if cli_value:
            return cli_value
        if template_value and is_template:
            return template_value
        if file_value and is_config_file:
            return file_value
        return cli_value

    @property
    def ignore_checks(self):
        return self._get_argument_value("ignore_checks", True, True)

    @property
    def include_checks(self):
        results = self._get_argument_value("include_checks", True, True)
        return ["W", "E"] + results

    @property
    def mandatory_checks(self):
        return self._get_argument_value("mandatory_checks", False, True)

    @property
    def include_experimental(self):
        return self._get_argument_value("include_experimental", True, True)

    @property
    def regions(self):
        results = self._get_argument_value("regions", True, True)
        if not results:
            default_region_env = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
            return [os.environ.get("AWS_REGION", default_region_env)]
        if "ALL_REGIONS" in results:
            return REGIONS
        return results

    @property
    def ignore_bad_template(self):
        return self._get_argument_value("ignore_bad_template", True, True)

    @property
    def debug(self):
        return self._get_argument_value("debug", False, False)

    @property
    def info(self):
        return self._get_argument_value("info", False, False)

    @property
    def format(self):
        return self._get_argument_value("format", False, True)

    @property
    def templates(self):
        """

        Returns a list of Cloudformation templates to lint.

        Order of precedence:
        - Filenames provided via `-t` CLI
        - Filenames specified in the config file.
        - Arguments provided via `cfn-lint` CLI.
        """

        all_filenames = []

        cli_alt_args = self._get_argument_value("template_alt", False, False)
        file_args = self._get_argument_value("templates", False, True)
        cli_args = self._get_argument_value("templates", False, False)

        if cli_alt_args:
            filenames = cli_alt_args
        elif file_args:
            filenames = file_args
        elif cli_args:
            filenames = cli_args
        else:
            # No filenames found, could be piped in or be using the api.
            return None

        # If we're still haven't returned, we've got templates to lint.
        # Build up list of templates to lint.
        self.templates_to_process = True

        if isinstance(filenames, str):
            filenames = [filenames]

        ignore_templates = self._ignore_templates()
        all_filenames.extend(self._glob_filenames(filenames))

        found_files = [i for i in all_filenames if i not in ignore_templates]
        LOGGER.debug(
            f"List of Cloudformation Templates to lint: {found_files} from {filenames}"
        )
        return found_files

    def _ignore_templates(self):
        ignore_template_args = self._get_argument_value("ignore_templates", False, True)
        if ignore_template_args:
            filenames = ignore_template_args
        else:
            return []

        # if only one is specified convert it to array
        if isinstance(filenames, str):
            filenames = [filenames]

        return self._glob_filenames(filenames)

    def _glob_filenames(self, filenames: Sequence[str]) -> list[str]:
        # handle different shells and Config files
        # some shells don't expand * and configparser won't expand wildcards
        all_filenames = []

        for filename in filenames:
            add_filenames = glob.glob(filename, recursive=True)

            if isinstance(add_filenames, list):
                all_filenames.extend(add_filenames)
            else:
                LOGGER.error(f"{filename} could not be processed by glob.glob")

        return sorted(list(map(str, map(Path, all_filenames))))

    @property
    def append_rules(self):
        return [_DEFAULT_RULESDIR] + self._get_argument_value(
            "append_rules", False, True
        )

    @property
    def override_spec(self):
        return self._get_argument_value("override_spec", False, True)

    @property
    def custom_rules(self):
        """custom_rules_spec"""
        return self._get_argument_value("custom_rules", False, True)

    @property
    def update_specs(self):
        return self._get_argument_value("update_specs", False, False)

    @property
    def patch_specs(self):
        return self._get_argument_value("patch_specs", False, False)

    @property
    def update_documentation(self):
        return self._get_argument_value("update_documentation", False, False)

    @property
    def update_iam_policies(self):
        return self._get_argument_value("update_iam_policies", False, False)

    @property
    def listrules(self):
        return self._get_argument_value("listrules", False, False)

    @property
    def configure_rules(self):
        return self._get_argument_value("configure_rules", True, True)

    @property
    def config_file(self):
        return self._get_argument_value("config_file", False, False)

    @property
    def build_graph(self):
        return self._get_argument_value("build_graph", False, False)

    @property
    def output_file(self):
        return self._get_argument_value("output_file", False, True)

    @property
    def registry_schemas(self):
        return self._get_argument_value("registry_schemas", False, True)

    @property
    def merge_configs(self):
        return self._get_argument_value("merge_configs", True, True)

    @property
    def non_zero_exit_code(self):
        return self._get_argument_value("non_zero_exit_code", False, False)

    @property
    def force(self):
        return self._get_argument_value("force", False, False)

    @property
    def templates_to_process(self):
        return self._templates_to_process

    @templates_to_process.setter
    def templates_to_process(self, value: bool):
        self._templates_to_process = value
