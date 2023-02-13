#!/usr/bin/env python
"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import json
import logging

import boto3
from samtranslator.translator.managed_policy_translator import \
    ManagedPolicyLoader

LOGGER = logging.getLogger('cfnlint')


def main():
    session = boto3.session.Session()
    client = session.client("iam", region_name="us-east-1")

    policyLoader = ManagedPolicyLoader(client)
    policyLoader.load()

    filename = "src/cfnlint/data/Serverless/ManagedPolicies.json"
    with open(filename, "w+", encoding="utf-8") as f:
        json.dump(
            policyLoader._policy_map,
            f,
            indent=1,
            sort_keys=True,
            separators=(",", ": "),
        )


if __name__ == "__main__":
    try:
        main()
    except (ValueError, TypeError):
        LOGGER.error(ValueError)
