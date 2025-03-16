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


_data = {}


def _clean_arn_formats(arn):
    arn_parts = arn.split(":", 5)

    resource = arn_parts[5]
    delimiter = None
    for d in [":", "/"]:
        if d in resource:
            delimiter = d

    if delimiter:
        resource_parts = []
        for resource_part in resource.split(delimiter):
            if "${" in resource_part:
                resource_parts.append(".*")
                break

            resource_parts.append(resource_part)

        arn_parts[5] = delimiter.join(resource_parts)

    return ":".join(arn_parts)


def _processes_a_service(name, data):
    _data[name] = {
        "Actions": {},
        "Resources": {},
    }

    for action in data.get("Actions", []):
        _data[name]["Actions"][action.get("Name").lower()] = {}
        if "Resources" in action:
            _data[name]["Actions"][action.get("Name").lower()] = {
                "Resources": list([i["Name"] for i in action["Resources"]])
            }

    for resource in data.get("Resources", []):
        _data[name]["Resources"][resource.get("Name").lower()] = {
            "ARNFormats": [
                _clean_arn_formats(arn) for arn in resource.get("ARNFormats")
            ],
        }
        if "ConditionKeys" in resource:
            _data[name]["Resources"][resource.get("Name").lower()]["ConditionKeys"] = (
                resource.get("ConditionKeys")
            )


def main():
    configure_logging()

    services = read_json_from_url(SERVICES_URL)
    for service in services:
        name = service.get("service")
        data = read_json_from_url(service.get("url"))
        _processes_a_service(name, data)

    filename = "src/cfnlint/data/AdditionalSpecs/Policies.json"
    with open(filename, "w+", encoding="utf-8") as f:
        json.dump(_data, f, indent=1, sort_keys=True, separators=(",", ": "))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, TypeError) as e:
        print(e)
        LOGGER.error(ValueError)
