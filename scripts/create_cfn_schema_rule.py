#!/usr/bin/env python
"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import argparse
import logging
import pathlib

from jinja2 import Environment, FileSystemLoader, select_autoescape

from cfnlint.helpers import ToPy, format_json_string, load_plugins

LOGGER = logging.getLogger("cfnlint")

RENAMES = {
    "ec2": "ectwo",
    "lambda": "lmbd",
}


def configure_logging():
    """Setup Logging"""
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    LOGGER.setLevel(logging.INFO)
    log_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    ch.setFormatter(log_formatter)

    # make sure all other log handlers are removed before adding it back
    for handler in LOGGER.handlers:
        LOGGER.removeHandler(handler)
    LOGGER.addHandler(ch)


def main():
    """main function"""
    configure_logging()

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--resource-type",
        metavar="resource_type",
        help="Resource type",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--rule-level",
        metavar="rule_level",
        help="Level of the rule",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--schema-name",
        metavar="schema_name",
        help="Schema name",
        type=str,
        required=True,
    )
    parser.add_argument(
        "--rule-name", metavar="rule_name", help="Rule name", type=str, required=True
    )
    parser.add_argument(
        "--type", metavar="type", help="rule type", type=str, required=False
    )

    args = parser.parse_args()

    if args.rule_level not in ["I", "W", "E"]:
        print(parser.usage())
        return

    if args.type and args.type not in ["only-one", "atleast-one"]:
        print(parser.usage())
        return

    path_root = (
        pathlib.Path(__file__).parent.parent / "src" / "cfnlint" / "rules" / "resources"
    )
    schema_root = (
        pathlib.Path(__file__).parent.parent
        / "src"
        / "cfnlint"
        / "data"
        / "schemas"
        / "extensions"
    )
    rules = load_plugins(
        path_root, "BaseCfnSchema", "cfnlint.rules.resources.properties"
    )
    # new rule id
    new_rule_id = 3600
    for rule in sorted(rules, key=lambda rule: int(rule.id[1:])):
        if args.rule_level == rule.id[0]:
            if new_rule_id == int(rule.id[1:]):
                new_rule_id += 1
            else:
                break

    env = Environment(
        loader=FileSystemLoader("./scripts/assets"), autoescape=select_autoescape()
    )
    template = env.get_template("rule.py")

    resource_type = ToPy(args.resource_type)
    resource_category = resource_type.py.split("_")[1]
    schema_path = f"{resource_type.py}/{args.schema_name}"
    schema_file = schema_root / f"{schema_path}.json"

    rule_folder = path_root / resource_category
    rule_folder.mkdir(exist_ok=True)
    if not (rule_folder / "__init__.py").is_file():
        LOGGER.info("Create folder %s", (rule_folder / "__init__.py"))
        with open(rule_folder / "__init__.py", mode="w+") as fh:
            fh.write(
                """\"\"\"
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
\"\"\"
"""
            )

    rule_file = rule_folder / f"{args.rule_name}.py"
    with open(rule_file, "x", encoding="utf8") as fh:
        LOGGER.info("Create rule file %s", rule_file)
        fh.write(
            template.render(
                rule_id=f"{args.rule_level}{new_rule_id}", schema_path=schema_path
            )
        )
        fh.write("\n")

    if not schema_file.parents[0].exists():
        LOGGER.info("Create folder %s", schema_file.parents[0])
        schema_file.parents[0].mkdir()
        open(schema_file.parents[0] / "__init__.py", "x", encoding="utf8").close()

    schema = {}
    if args.type == "only-one":
        schema = {
            "message": {"oneOf": "Specify only one ['Property1', 'Property2']"},
            "oneOf": [
                {"required": ["Property1"]},
                {"required": ["Property2"]},
            ],
        }

    with open(schema_file, "x", encoding="utf8") as fh:
        LOGGER.info("Create schema file %s", schema_file)
        fh.write(format_json_string(schema))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, TypeError) as e:
        print(e)
        LOGGER.error(ValueError)
