#!/usr/bin/env python
"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import json
import logging

import requests

LOGGER = logging.getLogger("cfnlint")

SERVICES_URL = "https://servicereference.us-east-1.amazonaws.com"


def configure_logging():
    """Setup Logging"""
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    LOGGER.setLevel(logging.WARNING)
    log_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    ch.setFormatter(log_formatter)

    # make sure all other log handlers are removed before adding it back
    for handler in LOGGER.handlers:
        LOGGER.removeHandler(handler)
    LOGGER.addHandler(ch)


def read_json_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

        json_data = response.json()
        return json_data

    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSONDecodeError: {e}")
        return None


_resource_schema = {
    "definitions": {
        "resources_asterisk": {"enum": []},
    },
    "if": {
        "properties": {
            "Action": {
                "else": {
                    "contains": {
                        "$ref": "#/definitions/resources_asterisk",
                        "minContains": 1,
                    },
                    "type": "array",
                },
                "if": {"type": "string"},
                "then": {"$ref": "#/definitions/resources_asterisk"},
            }
        },
        "required": ["Action"],
    },
    "then": {
        "properties": {
            "Resource": {
                "else": {
                    "contains": {"enum": ["*"]},
                    "minContains": 1,
                    "type": "array",
                },
                "if": {"type": "string"},
                "then": {"const": "*"},
            }
        }
    },
    "type": "object",
}


def _processes_a_service(name, data):
    for action in data.get("Actions", []):
        if not action.get("Resources", []):
            yield f"{name}:{action.get('Name')}"


def main():
    configure_logging()

    services = read_json_from_url(SERVICES_URL)
    resources_asterisk = []
    for service in services:
        name = service.get("service")
        data = read_json_from_url(service.get("url"))
        resources_asterisk.extend(list(_processes_a_service(name, data)))

    _resource_schema["definitions"]["resources_asterisk"]["enum"] = resources_asterisk

    filename = "src/cfnlint/data/schemas/other/iam/policy_statement_resources.json"
    with open(filename, "w+", encoding="utf-8") as f:
        json.dump(_resource_schema, f, indent=1, sort_keys=True, separators=(",", ": "))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, TypeError) as e:
        print(e)
        LOGGER.error(ValueError)
