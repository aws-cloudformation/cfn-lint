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

    def test_main_adds_sagemaker_hosting_extras_per_region(self):
        """SageMaker hosting extras land only in the regions they were verified in."""
        module = _load_update_specs_from_pricing()

        def product(location, usage_type, instance_name):
            return json.dumps(
                {
                    "product": {
                        "productFamily": "ML Instance",
                        "attributes": {
                            "location": location,
                            "locationType": "AWS Region",
                            "instanceName": instance_name,
                            "usagetype": usage_type,
                        },
                    }
                }
            )

        sagemaker_pages = [
            {
                "PriceList": [
                    product("US East (Ohio)", "USE2-Host:ml.m5.large", "ml.m5.large"),
                    product(
                        "Asia Pacific (Osaka)",
                        "APN3-Host:ml.m5.large",
                        "ml.m5.large",
                    ),
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
        hosting = outputs["aws_sagemaker_hosting"]

        # us-east-2 is verified, so the extras are unioned in
        self.assertIn("ml.m8g.large", hosting["us-east-2"])
        self.assertIn("ml.p5e.48xlarge", hosting["us-east-2"])
        # pricing derived values are kept
        self.assertIn("ml.m5.large", hosting["us-east-2"])
        # ap-northeast-3 does not offer ml.m8g.large, so it is not added there
        self.assertNotIn("ml.m8g.large", hosting["ap-northeast-3"])
        # a region with no pricing products is not introduced by the extras
        self.assertIn("us-east-1", module._SAGEMAKER_HOSTING_REGION_EXTRA)
        self.assertNotIn("us-east-1", hosting)

    def test_add_region_extras_adds_no_region(self):
        """The extras never introduce a region the pricing API did not return."""
        module = _load_update_specs_from_pricing()

        results = module.add_region_extras(
            {"us-east-1": set(["ml.m5.large"])},
            {"us-east-1": ["ml.m8g.large"], "us-west-1": ["ml.m8g.large"]},
        )

        self.assertEqual(results, {"us-east-1": set(["ml.m5.large", "ml.m8g.large"])})
