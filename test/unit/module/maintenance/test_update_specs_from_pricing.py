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

    def test_main_adds_sagemaker_api_types(self):
        """SageMaker enums keep API-valid types pricing files elsewhere."""
        module = _load_update_specs_from_pricing()

        def _sagemaker_product(usagetype, instance_name):
            return json.dumps(
                {
                    "product": {
                        "productFamily": "ML Instance",
                        "attributes": {
                            "location": "US East (Ohio)",
                            "locationType": "AWS Region",
                            "instanceName": instance_name,
                            "usagetype": usagetype,
                        },
                    }
                }
            )

        sagemaker_pages = [
            {
                "PriceList": [
                    _sagemaker_product("USE2-Cluster:ml.p5.48xlarge", "ml.p5.48xlarge"),
                    _sagemaker_product("USE2-Tsform:ml.m5.large", "ml.m5.large"),
                    _sagemaker_product("USE2-Host:ml.m5.large", "ml.m5.large"),
                    _sagemaker_product("USE2-Processing:ml.m5.large", "ml.m5.large"),
                ]
            }
        ]

        def get_paginator(service):
            return sagemaker_pages if service == "AmazonSageMaker" else []

        with (
            patch.object(module, "configure_logging"),
            patch.object(module, "get_paginator", side_effect=get_paginator),
            patch.object(module, "get_rds_pricing"),
            patch.object(module, "write_output") as write_output,
        ):
            module.main()

        outputs = {call.args[0]: call.args[2] for call in write_output.call_args_list}
        self.assertEqual(
            outputs["aws_sagemaker_cluster"],
            {"us-east-2": set(["ml.p5.48xlarge", "ml.p5e.48xlarge"])},
        )
        self.assertEqual(
            outputs["aws_sagemaker_transform"],
            {
                "us-east-2": set(
                    [
                        "ml.m5.large",
                        "ml.p3.2xlarge",
                        "ml.p3.8xlarge",
                        "ml.p3.16xlarge",
                        "ml.inf2.xlarge",
                        "ml.inf2.8xlarge",
                        "ml.inf2.24xlarge",
                        "ml.inf2.48xlarge",
                        "ml.trn1.2xlarge",
                        "ml.trn1.32xlarge",
                    ]
                )
            },
        )
        self.assertEqual(
            outputs["aws_sagemaker_hosting"],
            {
                "us-east-2": set(
                    [
                        "ml.m5.large",
                        "ml.m8g.medium",
                        "ml.m8g.large",
                        "ml.m8g.xlarge",
                        "ml.m8g.2xlarge",
                        "ml.m8g.4xlarge",
                        "ml.m8g.8xlarge",
                        "ml.m8g.12xlarge",
                        "ml.m8g.16xlarge",
                        "ml.m8g.24xlarge",
                        "ml.m8g.48xlarge",
                    ]
                )
            },
        )
        processing = outputs["aws_sagemaker_processing"]["us-east-2"]
        self.assertIn("ml.c8i.xlarge", processing)
        self.assertIn("ml.c8i.96xlarge", processing)
        self.assertIn("ml.m7i-flex.large", processing)
        self.assertIn("ml.c8i-flex.xlarge", processing)
        self.assertNotIn("ml.c8i.large", processing)
        self.assertEqual(len(processing), 44)

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
