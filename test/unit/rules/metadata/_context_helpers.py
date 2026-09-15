"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from cfnlint.decode import cfn_yaml
from cfnlint.rules.metadata.ContextMissing import ContextMissing
from cfnlint.template import Template


def match(rule, template_str):
    """Decode a template string and run one rule's match() against it."""
    decoded = cfn_yaml.loads(template_str)
    cfn = Template("test.yaml", decoded)
    return rule.match(cfn)


def decoded_template(template_str):
    """Decode a template string into a Template, for tests that reuse a rule."""
    return Template("test.yaml", cfn_yaml.loads(template_str))


def missing_rule():
    """ContextMissing: flags templates and architecture-relevant resources."""
    return ContextMissing()
