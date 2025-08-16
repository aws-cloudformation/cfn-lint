"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

import argparse
import copy
import functools
import glob
import json
import logging
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Sequence, TypedDict

from typing_extensions import Unpack

import cfnlint.decode.cfn_yaml
from cfnlint.context.parameters import ParameterSet
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
            parser.exit(1)


class ExtendKeyValuePairs(argparse.Action):
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

    def __call__(self, parser, namespace, values, option_string=None):
        try:
            items = {}
            for value in values:
                # split it into key and value
                key, value = value.split("=", 1)
                items[key.strip()] = value.strip()

            result = getattr(namespace, self.dest) + [items]
            setattr(namespace, self.dest, result)
        except Exception:  # pylint: disable=W0703
            parser.print_help()
            parser.exit(1)


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
                self.exit(1, f"{self.prog}: error: {message}\n")

        usage = (
            "\nBasic: cfn-lint test.yaml\n"
            "Ignore a rule: cfn-lint -i E3012 -- test.yaml\n"
            "Configure a rule: cfn-lint -x E3012:strict=true -t test.yaml\n"
            "Lint all yaml files in a folder: cfn-lint dir/**/*.yaml"
        )

        parser = ArgumentParser(description="CloudFormation Linter", usage=usage)
        parser.register("action", "extend", ExtendAction)
        parser.register("action", "rule_configuration", RuleConfigurationAction)
        parser.register("action", "extend_key_value", ExtendKeyValuePairs)

        standard = parser.add_argument_group("Standard")
        advanced = parser.add_argument_group("Advanced / Debugging")

        validation_group = standard.add_mutually_exclusive_group()
        parameter_group = standard.add_mutually_exclusive_group()

        # Allow the template to be passes as an optional or a positional argument
        standard.add_argument(
            "templates",
            metavar="TEMPLATE",
            nargs="*",
            help="The CloudFormation template to be linted",
        )
        validation_group.add_argument(
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
        validation_group.add_argument(
            "--deployment-files",
            dest="deployment_files",
            help="Deployment files",
            nargs="+",
            default=[],
            action="extend",
        )
        parameter_group.add_argument(
            "--parameters",
            dest="parameters",
            nargs="+",
            default=[],
            action="extend_key_value",
            help="A list of parameters",
        )
        validation_group.add_argument(
            "--parameter-files",
            dest="parameter_files",
            help="A list of parameter files",
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
        advanced.add_argument(
            "-L",
            "--list-templates",
            dest="listtemplates",
            default=False,
            action="store_true",
            help="List all the templates would have linted",
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
            action="rule_configuration",
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
            default=[],
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
                    "append_rules": list,
                    "configure_rules": dict,
                    "custom_rules": str,
                    "ignore_bad_template": bool,
                    "ignore_checks": list,
                    "include_checks": list,
                    "include_experimental": bool,
                    "override_spec": str,
                    "parameters": list,
                    "parameter_files": list,
                    "regions": list,
                }.items():
                    if key in configs:
                        if isinstance(configs[key], value):
                            defaults[key] = configs[key]

        self._template_args = defaults

    template_args = property(get_template_args, set_template_args)


class ManualArgs(TypedDict, total=False):
    append_rules: list[str]
    configure_rules: dict[str, dict[str, Any]]
    deployment_files: list[str]
    ignore_bad_template: bool
    ignore_checks: list[str]
    ignore_templates: list
    include_checks: list[str]
    include_experimental: bool
    mandatory_checks: list[str]
    merge_configs: bool
    non_zero_exit_code: str
    output_file: str
    parameter_files: list[str]
    parameters: list[ParameterSet]
    regions: list
    registry_schemas: list[str]
    template_parameters: list[dict[str, Any]]
    templates: list[str]


def _merge_configs(
    cli_value: Any, template_value: Any, file_value: Any, manual_value: Any
) -> Any:
    # the CLI will always have an empty list when the item is a list
    # we will use that to evaluate if we need to merge the lists
    if isinstance(cli_value, list):
        merged_list = cli_value.copy()
        if isinstance(template_value, list):
            merged_list.extend(template_value)
        if isinstance(file_value, list):
            merged_list.extend(file_value)
        if isinstance(manual_value, list):
            merged_list.extend(manual_value)
        return merged_list

    elif isinstance(cli_value, dict):
        merged_dict = cli_value.copy()
        if isinstance(template_value, dict):
            merged_dict.update(template_value)
        if isinstance(file_value, dict):
            merged_dict.update(file_value)
        if isinstance(manual_value, dict):
            merged_dict.update(manual_value)
        return merged_dict

    return None


# pylint: disable=too-many-public-methods
@dataclass(frozen=True)
class ConfigMixIn:
    """
    Immutable configuration with automatic caching.

    Drop-in replacement for the current ConfigMixIn using dataclass + cached_property
    for optimal performance without manual cache invalidation complexity.
    """

    # Init-only parameters (backward-compatible API)
    cli_args_list: list[str] | None = field(default=None)
    append_rules_init: list[str] = field(default_factory=list)
    configure_rules_init: dict[str, dict[str, Any]] = field(default_factory=dict)
    deployment_files_init: list[str] = field(default_factory=list)
    ignore_bad_template_init: bool = field(default=False)
    ignore_checks_init: list[str] = field(default_factory=list)
    ignore_templates_init: list = field(default_factory=list)
    include_checks_init: list[str] = field(default_factory=list)
    include_experimental_init: bool = field(default=False)
    mandatory_checks_init: list[str] = field(default_factory=list)
    merge_configs_init: bool = field(default=False)
    non_zero_exit_code_init: str = field(default="informational")
    output_file_init: str = field(default="")
    parameter_files_init: list[str] = field(default_factory=list)
    parameters_init: list = field(default_factory=list)
    regions_init: list = field(default_factory=list)
    registry_schemas_init: list[str] = field(default_factory=list)
    template_parameters_init: list[dict[str, Any]] = field(default_factory=list)
    templates_init: list[str] = field(default_factory=list)

    # Internal data
    _cli_args: CliArgs = field(init=False, repr=False)
    _template_args: dict = field(init=False, repr=False, default_factory=dict)
    _file_args: dict = field(init=False, repr=False, default_factory=dict)
    _manual_args: dict = field(init=False, repr=False, default_factory=dict)

    def __init__(self, cli_args: list[str] | None = None, **kwargs: Unpack[ManualArgs]):
        """Backward-compatible initialization."""
        # Set the init-only fields directly
        object.__setattr__(self, "cli_args_list", cli_args)
        object.__setattr__(self, "append_rules_init", kwargs.get("append_rules", []))
        object.__setattr__(
            self, "configure_rules_init", kwargs.get("configure_rules", {})
        )
        object.__setattr__(
            self, "deployment_files_init", kwargs.get("deployment_files", [])
        )
        object.__setattr__(
            self, "ignore_bad_template_init", kwargs.get("ignore_bad_template", False)
        )
        object.__setattr__(self, "ignore_checks_init", kwargs.get("ignore_checks", []))
        object.__setattr__(
            self, "ignore_templates_init", kwargs.get("ignore_templates", [])
        )
        object.__setattr__(
            self, "include_checks_init", kwargs.get("include_checks", [])
        )
        object.__setattr__(
            self, "include_experimental_init", kwargs.get("include_experimental", False)
        )
        object.__setattr__(
            self, "mandatory_checks_init", kwargs.get("mandatory_checks", [])
        )
        object.__setattr__(
            self, "merge_configs_init", kwargs.get("merge_configs", False)
        )
        object.__setattr__(
            self,
            "non_zero_exit_code_init",
            kwargs.get("non_zero_exit_code", "informational"),
        )
        object.__setattr__(self, "output_file_init", kwargs.get("output_file", ""))
        object.__setattr__(
            self, "parameter_files_init", kwargs.get("parameter_files", [])
        )
        object.__setattr__(self, "parameters_init", kwargs.get("parameters", []))
        object.__setattr__(self, "regions_init", kwargs.get("regions", []))
        object.__setattr__(
            self, "registry_schemas_init", kwargs.get("registry_schemas", [])
        )
        object.__setattr__(
            self, "template_parameters_init", kwargs.get("template_parameters", [])
        )
        object.__setattr__(self, "templates_init", kwargs.get("templates", []))

        # Call post_init to set up internal data
        self.__post_init__()

    def __post_init__(self):
        """Initialize internal data from init parameters."""
        # Initialize the base classes properly
        cli_args_obj = CliArgs(self.cli_args_list)
        object.__setattr__(self, "_cli_args", cli_args_obj)

        # ConfigFileArgs needs the config_file from CLI args
        config_file = getattr(cli_args_obj.cli_args, "config_file", None)
        file_args_obj = ConfigFileArgs(config_file=config_file)
        object.__setattr__(self, "_file_args", file_args_obj.file_args)

        # Template args (empty initially, will be set via set_template_args)
        object.__setattr__(self, "_template_args", {})

        # Manual args from init fields
        manual_args = {}
        field_mapping = {
            "append_rules": self.append_rules_init,
            "configure_rules": self.configure_rules_init,
            "deployment_files": self.deployment_files_init,
            "ignore_bad_template": self.ignore_bad_template_init,
            "ignore_checks": self.ignore_checks_init,
            "ignore_templates": self.ignore_templates_init,
            "include_checks": self.include_checks_init,
            "include_experimental": self.include_experimental_init,
            "mandatory_checks": self.mandatory_checks_init,
            "merge_configs": self.merge_configs_init,
            "non_zero_exit_code": self.non_zero_exit_code_init,
            "output_file": self.output_file_init,
            "parameter_files": self.parameter_files_init,
            "parameters": self.parameters_init,
            "regions": self.regions_init,
            "registry_schemas": self.registry_schemas_init,
            "template_parameters": self.template_parameters_init,
            "templates": self.templates_init,
        }

        for key, value in field_mapping.items():
            if value:  # Only include non-empty values
                manual_args[key] = value

        object.__setattr__(self, "_manual_args", manual_args)

    def __repr__(self):
        return format_json_string(
            {
                "append_rules": self.append_rules,
                "config_file": self.config_file,
                "configure_rules": self.configure_rules,
                "custom_rules": self.custom_rules,
                "debug": self.debug,
                "deployment_files": self.deployment_files,
                "format": self.format,
                "ignore_bad_template": self.ignore_bad_template,
                "ignore_checks": self.ignore_checks,
                "include_checks": self.include_checks,
                "include_experimental": self.include_experimental,
                "info": self.info,
                "mandatory_checks": self.mandatory_checks,
                "merge_configs": self.merge_configs,
                "non_zero_exit_code": self.non_zero_exit_code,
                "override_spec": self.override_spec,
                "parameter_files": self.parameter_files,
                "parameters": self.parameters,
                "patch_specs": self.patch_specs,
                "regions": self.regions,
                "registry_schemas": self.registry_schemas,
                "templates": self.templates,
            }
        )

    def __eq__(self, other):
        """Equality comparison for testing."""
        if not isinstance(other, ConfigMixIn):
            return False
        for key in [
            "configure_rules",
            "deployment_files",
            "ignore_bad_template",
            "ignore_checks",
            "include_checks",
            "include_experimental",
            "mandatory_checks",
            "merge_configs",
            "non_zero_exit_code",
            "output_file",
            "regions",
            "parameter_files",
            "parameters",
            "templates",
        ]:
            if getattr(self, key) != getattr(other, key):
                return False
        return True

    # Additional methods for compatibility
    def validate(self, allow_stdin: bool = False) -> None:
        """Validate the configuration for logical consistency."""
        # Get raw configuration values
        raw_templates = []
        if "templates" in self._manual_args:
            raw_templates = self._manual_args["templates"]
        else:
            cli_alt_args = self._get_argument_value("template_alt", False, False)
            cli_args = self._get_argument_value("templates", False, False)
            if cli_alt_args:
                raw_templates = cli_alt_args
            elif cli_args:
                raw_templates = cli_args

        # Ensure it's a list
        if isinstance(raw_templates, str):
            raw_templates = [raw_templates]
        raw_templates = raw_templates or []
        raw_deployment_files = (
            self._get_argument_value("deployment_files", False, False) or []
        )
        raw_parameters = self._get_argument_value("parameters", False, False) or {}
        raw_parameter_files = (
            self._get_argument_value("parameter_files", False, False) or []
        )

        # Check if no templates or deployment files are specified
        if not raw_templates and not raw_deployment_files and not allow_stdin:
            raise ValueError("No templates or deployment files specified")

        # Check for conflicting deployment files with other options
        if raw_deployment_files:
            if raw_templates or raw_parameters or raw_parameter_files:
                raise ValueError(
                    "Deployment files cannot be used with templates, parameters, "
                    "or parameter files"
                )

        # Check for conflicting parameter options
        if raw_parameters and raw_parameter_files:
            raise ValueError("Cannot specify both --parameters and --parameter-files")

        # Check for multiple templates with parameters
        if (raw_parameters or raw_parameter_files) and len(raw_templates) > 1:
            raise ValueError("Parameters can only be used with a single template")

    def _get_argument_value(
        self, arg_name: str, is_template: bool, is_config_file: bool
    ) -> Any:
        """Core configuration resolution logic with proper precedence."""
        # Access CLI args from the parsed cli_args object
        cli_value = getattr(self._cli_args.cli_args, arg_name, None)
        template_value = self._template_args.get(arg_name)
        file_value = self._file_args.get(arg_name)
        manual_value = self._manual_args.get(arg_name)

        # Handle configuration merging for list/dict types
        if arg_name != "merge_configs":
            if self.merge_configs:
                if isinstance(cli_value, (list, dict)):
                    return _merge_configs(
                        cli_value, template_value, file_value, manual_value
                    )

        # Apply precedence: manual > cli > template > file > cli_default
        if manual_value:
            return manual_value
        if cli_value:
            return cli_value
        if template_value and is_template:
            return template_value
        if file_value and is_config_file:
            return file_value
        return cli_value

    @functools.cached_property
    def ignore_checks(self) -> list[str]:
        result = self._get_argument_value("ignore_checks", True, True)
        return result if isinstance(result, list) else []

    @functools.cached_property
    def include_checks(self) -> list[str]:
        results = self._get_argument_value("include_checks", True, True)
        if not isinstance(results, list):
            results = []
        # Ensure results is definitely a list[str]
        validated_results: list[str] = [str(item) for item in results if item]
        return ["W", "E"] + validated_results

    @functools.cached_property
    def mandatory_checks(self) -> list[str]:
        result = self._get_argument_value("mandatory_checks", False, True)
        return result if isinstance(result, list) else []

    @functools.cached_property
    def include_experimental(self) -> bool:
        result = self._get_argument_value("include_experimental", True, True)
        return bool(result)

    @functools.cached_property
    def regions(self) -> list[str]:
        results = self._get_argument_value("regions", True, True)
        if not results:
            default_region_env = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
            region = os.environ.get("AWS_REGION", default_region_env) or "us-east-1"
            return [region]
        if isinstance(results, list) and "ALL_REGIONS" in results:
            return REGIONS
        return results if isinstance(results, list) else []

    @functools.cached_property
    def ignore_bad_template(self) -> bool:
        result = self._get_argument_value("ignore_bad_template", True, True)
        return bool(result)

    @functools.cached_property
    def debug(self) -> bool:
        result = self._get_argument_value("debug", False, True)
        return bool(result)

    @functools.cached_property
    def info(self) -> bool:
        result = self._get_argument_value("info", False, False)
        return bool(result)

    @functools.cached_property
    def format(self) -> str:
        result = self._get_argument_value("format", False, True)
        return str(result) if result else ""

    @functools.cached_property
    def templates(self) -> list[str] | None:
        """Resolved templates with complex precedence logic."""
        all_filenames = []

        cli_alt_args = self._get_argument_value("template_alt", False, False)
        file_args = self._get_argument_value("templates", False, True)
        cli_args = self._get_argument_value("templates", False, False)

        if "templates" in self._manual_args:
            filenames = self._manual_args["templates"]
        elif cli_alt_args:
            filenames = cli_alt_args
        elif cli_args:
            filenames = cli_args
        elif file_args:
            filenames = file_args
        else:
            return None

        # If we have no filenames at this point, return None
        if not filenames:
            return None

        if isinstance(filenames, str):
            filenames = [filenames]

        ignore_templates = self._ignore_templates()
        all_filenames.extend(self._glob_filenames(filenames))

        found_files = [i for i in all_filenames if i not in ignore_templates]
        return found_files

    def _ignore_templates(self) -> list[str]:
        """Helper for templates property."""
        ignore_template_args = self._get_argument_value("ignore_templates", False, True)
        if ignore_template_args:
            filenames = ignore_template_args
        else:
            return []

        if isinstance(filenames, str):
            filenames = [filenames]

        return self._glob_filenames(filenames, False)

    def _glob_filenames(
        self, filenames: Sequence[str], raise_exception: bool = True
    ) -> list[str]:
        """Handle file globbing with error handling."""
        if not filenames:
            return []

        all_filenames = []
        for filename in filenames:
            add_filenames = glob.glob(filename, recursive=True)
            if not add_filenames and not self.ignore_bad_template:
                if raise_exception:
                    raise ValueError(f"{filename} could not be processed by glob.glob")
            all_filenames.extend(add_filenames)

        return sorted(list(map(str, map(Path, all_filenames))))

    def with_template_args(self, template_args: dict) -> "ConfigMixIn":
        """Create a new immutable ConfigMixIn instance with template args applied."""
        new_config = ConfigMixIn(cli_args=self.cli_args_list, **self._manual_args)

        template_parser = TemplateArgs(template_args)
        object.__setattr__(new_config, "_template_args", template_parser.template_args)

        return new_config

    @functools.cached_property
    def append_rules(self) -> list[str]:
        append_rules = self._get_argument_value("append_rules", False, True) or []
        return [_DEFAULT_RULESDIR] + append_rules

    @functools.cached_property
    def parameter_files(self) -> list[str]:
        filenames = self._get_argument_value("parameter_files", True, True)
        return self._glob_filenames(filenames, raise_exception=True)

    @functools.cached_property
    def parameters(self) -> list[ParameterSet]:
        parameter_sets = self._get_argument_value("parameters", True, True)
        results: list[ParameterSet] = []
        for parameter_set in parameter_sets:
            if isinstance(parameter_set, ParameterSet):
                results.append(parameter_set)
            else:
                results.append(ParameterSet(source=None, parameters=parameter_set))
        return results

    @functools.cached_property
    def listtemplates(self) -> bool:
        result = self._get_argument_value("listtemplates", False, False)
        return bool(result)

    @functools.cached_property
    def override_spec(self) -> str:
        result = self._get_argument_value("override_spec", False, True)
        return str(result) if result else ""

    @functools.cached_property
    def custom_rules(self) -> str:
        result = self._get_argument_value("custom_rules", False, True)
        return str(result) if result else ""

    @functools.cached_property
    def update_specs(self) -> bool:
        result = self._get_argument_value("update_specs", False, False)
        return bool(result)

    @functools.cached_property
    def patch_specs(self) -> bool:
        result = self._get_argument_value("patch_specs", False, False)
        return bool(result)

    @functools.cached_property
    def update_documentation(self) -> bool:
        result = self._get_argument_value("update_documentation", False, False)
        return bool(result)

    @functools.cached_property
    def update_iam_policies(self) -> bool:
        result = self._get_argument_value("update_iam_policies", False, False)
        return bool(result)

    @functools.cached_property
    def listrules(self) -> bool:
        result = self._get_argument_value("listrules", False, False)
        return bool(result)

    @functools.cached_property
    def configure_rules(self) -> dict[str, dict[str, Any]]:
        result = self._get_argument_value("configure_rules", True, True)
        return result if isinstance(result, dict) else {}

    @functools.cached_property
    def deployment_files(self) -> list[str]:
        deployment_files = self._get_argument_value("deployment_files", False, True)
        return self._glob_filenames(deployment_files, True)

    @functools.cached_property
    def config_file(self) -> str:
        result = self._get_argument_value("config_file", False, False)
        return str(result) if result else ""

    @functools.cached_property
    def build_graph(self) -> bool:
        result = self._get_argument_value("build_graph", False, False)
        return bool(result)

    @functools.cached_property
    def output_file(self) -> str:
        result = self._get_argument_value("output_file", False, True)
        return str(result) if result else ""

    @functools.cached_property
    def registry_schemas(self) -> list[str]:
        result = self._get_argument_value("registry_schemas", False, True)
        return result if isinstance(result, list) else []

    @functools.cached_property
    def merge_configs(self) -> bool:
        result = self._get_argument_value("merge_configs", True, True)
        return bool(result)

    @functools.cached_property
    def non_zero_exit_code(self) -> str:
        result = self._get_argument_value("non_zero_exit_code", False, False)
        return str(result) if result else "informational"

    @functools.cached_property
    def force(self) -> bool:
        result = self._get_argument_value("force", False, False)
        return bool(result)

    @property
    def parser(self):
        """Access to the argument parser for backward compatibility."""
        return self._cli_args.parser

    # Evolution methods for backward compatibility and internal use
    def evolve(self, **kwargs: Unpack[ManualArgs]) -> "ConfigMixIn":
        """Create new ConfigMixIn with updated manual args (backward compatible)."""
        # Merge existing manual args with new kwargs
        merged_args = self._manual_args.copy()
        merged_args.update(kwargs)
        return ConfigMixIn(cli_args=self.cli_args_list, **merged_args)
