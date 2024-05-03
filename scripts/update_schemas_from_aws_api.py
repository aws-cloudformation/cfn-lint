#!/usr/bin/env python
"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0

Updates our dynamic patches from the pricing API
This script requires Boto3 and Credentials to call the Pricing API
"""
import json
import logging

import boto3
from botocore.client import Config

LOGGER = logging.getLogger("cfnlint")


session = boto3.session.Session()
config = Config(retries={"max_attempts": 10})
client = session.client("rds", region_name="us-east-1", config=config)


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


def write_output(resource, filename, obj):
    filename = f"src/cfnlint/data/schemas/extensions/{resource}/{filename}.json"
    obj["_description"] = ("Automatically updated using aws api",)

    with open(filename, "w+", encoding="utf-8") as f:
        json.dump(obj, f, indent=1, sort_keys=True, separators=(",", ": "))
        f.write("\n")


def write_db_cluster(results):
    schema = {"allOf": []}

    engines = ["aurora-mysql", "aurora-postgresql", "mysql", "postgres"]

    schema["allOf"].append(
        {
            "if": {
                "properties": {
                    "Engine": {
                        "type": "string",
                    }
                },
                "required": ["Engine"],
            },
            "then": {
                "properties": {
                    "Engine": {
                        "enum": sorted(engines),
                    }
                }
            },
        }
    )

    for engine in engines:
        if not results.get(engine):
            continue
        schema["allOf"].append(
            {
                "if": {
                    "properties": {
                        "Engine": {
                            "const": engine,
                        },
                        "EngineVersion": {"type": ["string", "number"]},
                    },
                    "required": ["Engine", "EngineVersion"],
                },
                "then": {
                    "properties": {
                        "EngineVersion": {"enum": sorted(results.get(engine))}
                    }
                },
            }
        )

    write_output("aws_rds_dbcluster", "engine_version", schema)


def write_db_instance(results):
    schema = {"allOf": []}

    engines = [
        "aurora-mysql",
        "aurora-postgresql",
        "custom-oracle-ee",
        "custom-oracle-ee-cdb",
        "custom-sqlserver-ee",
        "custom-sqlserver-se",
        "custom-sqlserver-web",
        "db2-ae",
        "db2-se",
        "mariadb",
        "mysql",
        "oracle-ee",
        "oracle-ee-cdb",
        "oracle-se2",
        "oracle-se2-cdb",
        "postgres",
        "sqlserver-ee",
        "sqlserver-se",
        "sqlserver-ex",
        "sqlserver-web",
    ]

    schema["allOf"].append(
        {
            "if": {
                "properties": {
                    "Engine": {
                        "type": "string",
                    }
                },
                "required": ["Engine"],
            },
            "then": {
                "properties": {
                    "Engine": {
                        "enum": sorted(engines),
                    }
                }
            },
        }
    )

    for engine in engines:
        if not results.get(engine):
            continue
        schema["allOf"].append(
            {
                "if": {
                    "properties": {
                        "Engine": {
                            "const": engine,
                        },
                        "EngineVersion": {
                            "type": ["string", "number"],
                        },
                    },
                    "required": ["Engine", "EngineVersion"],
                },
                "then": {
                    "properties": {
                        "EngineVersion": {"enum": sorted(results.get(engine))}
                    }
                },
            }
        )

    write_output("aws_rds_dbinstance", "engine_version", schema)


def main():
    """main function"""
    configure_logging()

    results = {}
    for page in client.get_paginator("describe_db_engine_versions").paginate():
        for version in page.get("DBEngineVersions"):
            engine = version.get("Engine")
            engine_version = version.get("EngineVersion")
            if engine not in results:
                results[engine] = []
            results[engine].append(engine_version)

    write_db_cluster(results)
    write_db_instance(results)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, TypeError) as e:
        LOGGER.error(e)
