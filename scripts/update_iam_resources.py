#!/usr/bin/env python
"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""
import json
import logging
from copy import deepcopy

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


_if_schema = {
    "if": {
        "properties": {
            "Action": {
                "else": {
                    "contains": {
                        "const": "",
                        "minContains": 1,
                    },
                    "type": "array",
                },
                "if": {"type": "string"},
                "then": {"const": ""},
            }
        },
        "required": ["Action"],
    },
    "then": {
        "properties": {
            "Resource": {
                "else": {
                    "contains": {"$ref": "#/definitions/shapes"},
                    "minContains": 1,
                    "type": "array",
                },
                "if": {"type": "string"},
                "then": {"$ref": "#/definitions/shapes"},
            }
        }
    },
}

_resource_schema = {
    "definitions": {"resources_asterisk": {"enum": []}, "resources": {}},
    "allOf": [
        {
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
        },
    ],
    "type": "object",
}


def _processes_a_service(name, data):
    resource_actions = {}
    for action in data.get("Actions", []):
        resources = action.get("Resources", [])
        action_name = f"{name}:{action['Name']}"
        if not resources:
            _resource_schema["definitions"]["resources_asterisk"]["enum"].append(
                action_name
            )
            continue

        for resource in resources:
            resource_name = resource.get("Name")
            if not resource_name:
                continue

            if resource_name not in resource_actions:
                resource_actions[resource_name] = []

            resource_actions[resource_name].append(action_name)

    for resource, actions in resource_actions.items():
        resource_name = f"{name}:{resource}"
        _allof_if_schema = deepcopy(_if_schema)
        _allof_if_schema["if"]["properties"]["Action"]["then"]["enum"] = actions
        _allof_if_schema["if"]["properties"]["Action"]["else"]["contains"][
            "enum"
        ] = actions
        _allof_if_schema["then"]["properties"]["Resource"]["then"][
            "$ref"
        ] = f"#/definitions/shapes/{resource_name}"
        _allof_if_schema["then"]["properties"]["Resource"]["else"]["contains"][
            "$ref"
        ] = f"#/definitions/shapes/{resource_name}"

        _resource_schema["allOf"].append(_allof_if_schema)

    for resource in data.get("Resources", []):
        resource_name = f"{name}:{resource.get('Name')}"
        _resource_schema["definitions"]["resources"][resource_name] = {
            "arn_formats": resource.get("ARNFormats")
        }

    # for shape in data.get("Shapes", []):
    #    _allof_if_schema = deepcopy(_if_schema)
    #    _allof_if_schema["if"]["properties"]["Action"]["then"]["const"] = action_name
    #    _allof_if_schema["if"]["properties"]["Action"]["else"]["contains"]["const"] = action_name
    #    _allof_if_schema["then"]["properties"]["Resource"]["then"]["$ref"] = f"#/definitions/shapes/{name}:{shape_name}"
    #    _allof_if_schema["then"]["properties"]["Resource"]["else"]["contains"]["$ref"] = f"#/definitions/shapes/{name}:{shape_name}"
    #
    # _resource_schema["allOf"].append(_allof_if_schema)


def main():
    configure_logging()

    services = read_json_from_url(SERVICES_URL)
    for service in services:
        name = service.get("service")
        data = read_json_from_url(service.get("url"))
        _processes_a_service(name, data)

    filename = "src/cfnlint/data/schemas/other/iam/policy_statement_resources.json"
    with open(filename, "w+", encoding="utf-8") as f:
        json.dump(_resource_schema, f, indent=1, sort_keys=True, separators=(",", ": "))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, TypeError) as e:
        print(e)
        LOGGER.error(ValueError)
