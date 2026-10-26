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
