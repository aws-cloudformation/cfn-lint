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
rds_client = session.client("rds", region_name="us-east-1", config=config)
elasticache_client = session.client(
    "elasticache", region_name="us-east-1", config=config
)

_ENGINE_SUPPORTED = [
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
    obj["description"] = "Automatically updated using aws api"

    with open(filename, "w+", encoding="utf-8") as f:
        json.dump(obj, f, indent=1, sort_keys=True, separators=(",", ": "))
        f.write("\n")


def write_db_cluster(results):
    schema = {"allOf": []}

    engines = sorted(["aurora-mysql", "aurora-postgresql", "mysql", "postgres"])

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

        engine_versions = sorted(results.get(engine).keys())
        if engine == "aurora-mysql":
            for engine_version in engine_versions.copy():
                sub_engine_version = ".".join(engine_version.split(".")[0:2])
                if sub_engine_version not in engine_versions:
                    engine_versions.append(sub_engine_version)
            engine_versions = sorted(engine_versions)
        if engine == "aurora-postgresql":
            for engine_version in engine_versions.copy():
                sub_engine_version = engine_version.split(".")[0]
                if sub_engine_version not in engine_versions:
                    engine_versions.append(sub_engine_version)
            engine_versions = sorted(engine_versions)

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
                "then": {"properties": {"EngineVersion": {"enum": engine_versions}}},
            }
        )

    write_output("aws_rds_dbcluster", "engine_version", schema)


def write_db_cluster_deprecated(deprecated_results):
    schema = {"allOf": []}

    engines = sorted(["aurora-mysql", "aurora-postgresql", "mysql", "postgres"])

    for engine in engines:
        if not deprecated_results.get(engine):
            continue

        engine_versions = sorted(deprecated_results.get(engine).keys())
        if engine == "aurora-mysql":
            for engine_version in engine_versions.copy():
                sub_engine_version = ".".join(engine_version.split(".")[0:2])
                if sub_engine_version not in engine_versions:
                    engine_versions.append(sub_engine_version)
            engine_versions = sorted(engine_versions)
        if engine == "aurora-postgresql":
            for engine_version in engine_versions.copy():
                sub_engine_version = engine_version.split(".")[0]
                if sub_engine_version not in engine_versions:
                    engine_versions.append(sub_engine_version)
            engine_versions = sorted(engine_versions)

        if engine_versions:  # Only add if there are deprecated versions
            schema["allOf"].append(
                {
                    "if": {
                        "properties": {
                            "Engine": {
                                "const": engine,
                            },
                            "EngineVersion": {
                                "type": ["string", "number"],
                                "enum": engine_versions,
                            },
                        },
                        "required": ["Engine", "EngineVersion"],
                    },
                    "then": False,  # This will trigger the warning rule
                }
            )

    write_output("aws_rds_dbcluster", "engine_version_deprecated", schema)


def write_db_instance(results):
    schema = {"allOf": []}

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
                        "enum": sorted(_ENGINE_SUPPORTED),
                    }
                }
            },
        }
    )

    for engine, engine_details in sorted(results.items()):
        if not results.get(engine):
            continue

        engine_versions = sorted(list(engine_details.keys()))
        if engine == "postgres":
            for engine_version in engine_versions.copy():
                major_engine_version = ".".join(engine_version.split(".")[0:1])
                if major_engine_version not in engine_versions:
                    engine_versions.append(major_engine_version)
            engine_versions = sorted(engine_versions)
        if engine == "aurora-mysql":
            for engine_version in engine_versions.copy():
                sub_engine_version = ".".join(engine_version.split(".")[0:2])
                if sub_engine_version not in engine_versions:
                    engine_versions.append(sub_engine_version)
            engine_versions = sorted(engine_versions)
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
                    "properties": {"EngineVersion": {"enum": sorted(engine_versions)}}
                },
            }
        )

    write_output("aws_rds_dbinstance", "engine_version", schema)


def write_db_instance_deprecated(deprecated_results):
    schema = {"allOf": []}

    engines = sorted(["aurora-mysql", "aurora-postgresql", "mysql", "postgres"])

    for engine in engines:
        if not deprecated_results.get(engine):
            continue

        engine_versions = sorted(list(deprecated_results.get(engine).keys()))
        if engine == "postgres":
            for engine_version in engine_versions.copy():
                major_engine_version = ".".join(engine_version.split(".")[0:1])
                if major_engine_version not in engine_versions:
                    engine_versions.append(major_engine_version)
            engine_versions = sorted(engine_versions)
        if engine == "aurora-mysql":
            for engine_version in engine_versions.copy():
                sub_engine_version = ".".join(engine_version.split(".")[0:2])
                if sub_engine_version not in engine_versions:
                    engine_versions.append(sub_engine_version)
            engine_versions = sorted(engine_versions)

        if engine_versions:  # Only add if there are deprecated versions
            schema["allOf"].append(
                {
                    "if": {
                        "properties": {
                            "Engine": {
                                "const": engine,
                            },
                            "EngineVersion": {
                                "type": ["string", "number"],
                                "enum": engine_versions,
                            },
                        },
                        "required": ["Engine", "EngineVersion"],
                    },
                    "then": False,  # This will trigger the warning rule
                }
            )

    write_output("aws_rds_dbinstance", "engine_version_deprecated", schema)


def write_db_instance_version_dbinstanceclass(results):
    schema = {"allOf": []}

    def _create_schema(engine, engine_version, db_instance_classes):
        v_parts = engine_version.split(".")
        engine_pattern = (
            f"^({v_parts[0]}\.{v_parts[1]}\..+|{v_parts[0]}\.{v_parts[1]})$"
        )
        return {
            "if": {
                "properties": {
                    "Engine": {
                        "type": "string",
                        "const": engine,
                    },
                    "EngineVersion": {
                        "type": "string",
                        "pattern": engine_pattern,
                    },
                    "DBInstanceClass": {
                        "type": "string",
                    },
                },
                "required": ["Engine", "EngineVersion", "DBInstanceClass"],
            },
            "then": {
                "properties": {
                    "DBInstanceClass": {
                        "enum": sorted(db_instance_classes),
                    }
                }
            },
        }

    for engine, engine_details in sorted(results.items()):
        for engine_version, engine_version_details in sorted(engine_details.items()):
            db_instance_classes = engine_version_details.get("DBInstanceClass")
            if not db_instance_classes:
                continue
            if not results.get(engine):
                continue

            db_instance_classes = sorted(db_instance_classes)
            schema["allOf"].append(
                _create_schema(engine, engine_version, db_instance_classes)
            )

    write_output("aws_rds_dbinstance", "db_instance_class", schema)


def write_elasticache_engines(results):
    schema = {"allOf": []}

    engines = [
        "memcached",
        "redis",
        "valkey",
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

        engine_versions = sorted(results.get(engine))
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
                    "properties": {"EngineVersion": {"enum": sorted(engine_versions)}}
                },
            }
        )

    write_output("aws_elasticache_cachecluster", "engine_version", schema)


def rds_api():
    results = {}
    deprecated_results = {}
    available_results = {}

    # Get all versions including deprecated ones
    for page in rds_client.get_paginator("describe_db_engine_versions").paginate(
        IncludeAll=True
    ):
        for version in page.get("DBEngineVersions"):
            engine = version.get("Engine")
            if engine not in _ENGINE_SUPPORTED:
                continue
            engine_version = version.get("EngineVersion")
            status = version.get("Status", "available")

            if engine not in results:
                results[engine] = {}
            results[engine][engine_version] = {}

            # Track deprecated versions separately
            if status == "deprecated":
                if engine not in deprecated_results:
                    deprecated_results[engine] = {}
                deprecated_results[engine][engine_version] = {}
            else:
                # Track available versions for DB instance options
                if engine not in available_results:
                    available_results[engine] = {}
                available_results[engine][engine_version] = {}

    write_db_cluster(results)
    write_db_cluster_deprecated(deprecated_results)
    write_db_instance(results)
    write_db_instance_deprecated(deprecated_results)

    results_db_instance_class = dict.fromkeys(available_results.keys(), dict())
    for engine, versions in available_results.items():
        LOGGER.info(f"Starting RDS DB options collection for engine {engine!r}")
        for engine_version in versions.keys():
            minor_engine_verison = ".".join(engine_version.split(".")[:2])
            if minor_engine_verison in results_db_instance_class[engine]:
                results_db_instance_class[engine][minor_engine_verison][
                    "EngineVersions"
                ].add(engine_version)
            else:
                results_db_instance_class[engine][minor_engine_verison] = {
                    "EngineVersions": set([engine_version]),
                    "DBInstanceClass": set(),
                }

            for page in rds_client.get_paginator(
                "describe_orderable_db_instance_options"
            ).paginate(Engine=engine, EngineVersion=engine_version):
                for options in page.get("OrderableDBInstanceOptions"):
                    db_instance_class = options.get("DBInstanceClass")
                    results_db_instance_class[engine][minor_engine_verison][
                        "DBInstanceClass"
                    ].add(db_instance_class)

    write_db_instance_version_dbinstanceclass(results_db_instance_class)


def elasticache_api():
    results = {}
    for page in elasticache_client.get_paginator(
        "describe_cache_engine_versions"
    ).paginate():
        for version in page.get("CacheEngineVersions"):
            engine = version.get("Engine")
            engine_version = version.get("EngineVersion")
            if engine not in results:
                results[engine] = []
            results[engine].append(engine_version)

    write_elasticache_engines(results)


def main():
    """main function"""
    configure_logging()
    LOGGER.info("Starting RDS data collection")
    rds_api()
    LOGGER.info("Starting Elasticache data collection")
    elasticache_api()


if __name__ == "__main__":
    try:
        main()
    except (ValueError, TypeError) as e:
        LOGGER.error(e)
