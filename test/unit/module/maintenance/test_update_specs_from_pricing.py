"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import importlib.util
import json
from pathlib import Path
from test.testlib.testcase import BaseTestCase
from unittest.mock import patch


def _load_update_specs_from_pricing():
    path = Path(__file__).parents[4] / "scripts" / "update_specs_from_pricing.py"
    spec = importlib.util.spec_from_file_location("update_specs_from_pricing", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestUpdateSpecsFromPricing(BaseTestCase):
    """Used for testing pricing spec generation."""

    def test_main_adds_serverless_to_docdb(self):
        """DocumentDB gets db.serverless, which has no instance pricing."""
        module = _load_update_specs_from_pricing()
        docdb_pages = [
            {
                "PriceList": [
                    json.dumps(
                        {
                            "product": {
                                "productFamily": "Database Instance",
                                "attributes": {
                                    "location": "US East (N. Virginia)",
                                    "locationType": "AWS Region",
                                    "instanceType": "db.r6g.large",
                                },
                            }
                        }
                    )
                ]
            }
        ]

        def get_paginator(service):
            return docdb_pages if service == "AmazonDocDB" else []

        with (
            patch.object(module, "configure_logging"),
            patch.object(module, "get_paginator", side_effect=get_paginator),
            patch.object(module, "get_rds_pricing"),
            patch.object(module, "write_output") as write_output,
        ):
            module.main()

        outputs = {call.args[0]: call.args[2] for call in write_output.call_args_list}
        self.assertEqual(
            outputs["aws_docdb_dbinstance"],
            {"us-east-1": set(["db.serverless", "db.r6g.large"])},
        )

    def test_get_results_copies_default_values_per_region(self):
        """Default values stay isolated between generated region enums."""
        module = _load_update_specs_from_pricing()
        pages = [
            {
                "PriceList": [
                    json.dumps(
                        {
                            "product": {
                                "productFamily": "Database Instance",
                                "attributes": {
                                    "location": "US East (N. Virginia)",
                                    "locationType": "AWS Region",
                                    "instanceType": "db.r5.large",
                                },
                            }
                        }
                    ),
                    json.dumps(
                        {
                            "product": {
                                "productFamily": "Database Instance",
                                "attributes": {
                                    "location": "EU (Ireland)",
                                    "locationType": "AWS Region",
                                    "instanceType": "db.r6g.large",
                                },
                            }
                        }
                    ),
                ]
            }
        ]

        with patch.object(module, "get_paginator", return_value=pages):
            results = module.get_results(
                "AmazonNeptune",
                ["Database Instance"],
                default=set(["db.serverless"]),
            )

        self.assertEqual(results["us-east-1"], set(["db.serverless", "db.r5.large"]))
        self.assertEqual(results["eu-west-1"], set(["db.serverless", "db.r6g.large"]))

    def test_get_mq_pricing_expands_abbreviated_sizes(self):
        """Sizes the usage type shortens to "xl" get their full API names."""
        module = _load_update_specs_from_pricing()
        usage_types = [
            "mq.m5.large",
            "mq.m5.2xl",
            "mq.m5.4xl",
            "mq.m7g.xlarge",
            "mq.m7g.2xl",
            "mq.m7g.16xl",
            "mq.m7i.4xl",
        ]
        pages = [
            {
                "PriceList": [
                    json.dumps(
                        {
                            "product": {
                                "productFamily": "Broker Instances",
                                "attributes": {
                                    "location": "US East (N. Virginia)",
                                    "usagetype": f"USE1-Broker:{usage_type}",
                                },
                            }
                        }
                    )
                    for usage_type in usage_types
                ]
            }
        ]

        with patch.object(module, "get_paginator", return_value=pages):
            results = module.get_mq_pricing()

        self.assertEqual(
            results["us-east-1"],
            set(
                [
                    "mq.m5.large",
                    "mq.m5.2xlarge",
                    "mq.m5.4xlarge",
                    "mq.m7g.xlarge",
                    "mq.m7g.2xlarge",
                    "mq.m7g.16xlarge",
                    "mq.m7i.4xlarge",
                ]
            ),
        )

    def test_sagemaker_api_instance_types_resolve_every_shape(self):
        """Every mapped shape exists in the SageMaker service model."""
        module = _load_update_specs_from_pricing()

        results = module.get_sagemaker_api_instance_types()

        self.assertEqual(
            sorted(results),
            [
                "aws_sagemaker_cluster",
                "aws_sagemaker_hosting",
                "aws_sagemaker_processing",
                "aws_sagemaker_transform",
            ],
        )
        for resource, instance_types in results.items():
            self.assertIn("ml.m5.large", instance_types, resource)

    def test_main_adds_api_instance_types_to_every_sagemaker_region(self):
        """The Price List omits types the SageMaker API accepts."""
        module = _load_update_specs_from_pricing()
        sagemaker_pricing = {
            "us-east-1": {
                "Cluster": set(["ml.priced.cluster"]),
                "Host": set(["ml.priced.host"]),
                "Processing": set(["ml.priced.processing"]),
                "Tsform": set(["ml.priced.transform"]),
            },
            "eu-west-1": {
                "Cluster": set(["ml.priced.cluster"]),
                "Host": set(["ml.priced.host"]),
                "Processing": set(["ml.priced.processing"]),
                "Tsform": set(["ml.priced.transform"]),
            },
        }
        api_types = {
            "aws_sagemaker_cluster": set(["ml.api.cluster"]),
            "aws_sagemaker_hosting": set(["ml.api.host"]),
            "aws_sagemaker_processing": set(["ml.api.processing"]),
            "aws_sagemaker_transform": set(["ml.api.transform"]),
        }

        with (
            patch.object(module, "configure_logging"),
            patch.object(module, "get_paginator", return_value=[]),
            patch.object(module, "get_rds_pricing"),
            patch.object(
                module, "get_sagemaker_pricing", return_value=sagemaker_pricing
            ),
            patch.object(
                module, "get_sagemaker_api_instance_types", return_value=api_types
            ),
            patch.object(module, "write_output") as write_output,
        ):
            module.main()

        outputs = {call.args[0]: call.args[2] for call in write_output.call_args_list}
        for resource, suffix in [
            ("aws_sagemaker_cluster", "cluster"),
            ("aws_sagemaker_hosting", "host"),
            ("aws_sagemaker_processing", "processing"),
            ("aws_sagemaker_transform", "transform"),
        ]:
            expected = set([f"ml.priced.{suffix}", f"ml.api.{suffix}"])
            self.assertEqual(
                outputs[resource],
                {"us-east-1": expected, "eu-west-1": expected},
                resource,
            )
