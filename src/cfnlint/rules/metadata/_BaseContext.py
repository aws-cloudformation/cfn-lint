"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

# Shared infrastructure for the Context metadata validation rules
# (I4010/I4011/I4012): CDK/incidental detection, resource iteration, and the
# common config surface. Rule-specific logic lives in each rule's own file.
#
# CDK-synthesized templates are skipped entirely (detected by AWS::CDK::Metadata
# or aws:cdk:path). The user authored L2/L3 constructs, not raw CloudFormation.

from __future__ import annotations

import re
from typing import Any

CONTEXT_KEY = "com.aws.cloudformation.Context"
_CONTEXT_DISPLAY = "Metadata.com.aws.cloudformation.Context"

# Incidental resources: CDK helpers no author chose. CDK sees structure; cfn-lint
# sees only names, so it approximates via patterns. Extend with config option
# additional_incidental_patterns. The AwsCustomResource singleton ID is fixed
# (changing it orphans deployed functions).
_CDK_AWS_CUSTOM_RESOURCE_SINGLETON_ID = "AWS679f53fac002430cb0da5b7982bd2287"

_INCIDENTAL_PATH_PATTERN = re.compile(
    r"LogRetention|(?:^|/)Provider(?:/|$)|framework-onEvent|framework-isComplete"
    rf"|framework-onTimeout|{_CDK_AWS_CUSTOM_RESOURCE_SINGLETON_ID}"
)
# CFN strips hyphens at synth (framework-onEvent -> frameworkonEvent).
_INCIDENTAL_ID_PATTERN = re.compile(
    r"^LogRetention|(?<=[a-z])Provider(?=framework)"
    r"|frameworkonEvent|frameworkisComplete"
    rf"|frameworkonTimeout|^{_CDK_AWS_CUSTOM_RESOURCE_SINGLETON_ID}$"
)
_CDK_METADATA_TYPE = "AWS::CDK::Metadata"
_CDK_METADATA_LOGICAL_ID = "CDKMetadata"
_CDK_PATH_KEY = "aws:cdk:path"

_PATTERNS_CONFIG: dict[str, Any] = {"default": [], "type": "list", "itemtype": "string"}


def _is_incidental(
    logical_id: str, resource: dict[str, Any], extra_patterns: list[str]
) -> bool:
    """True when the resource is incidental/framework per the targeting policy."""
    if resource.get("Type") == _CDK_METADATA_TYPE:
        return True
    if logical_id == _CDK_METADATA_LOGICAL_ID:
        return True
    metadata = resource.get("Metadata")
    cdk_path = metadata.get(_CDK_PATH_KEY) if isinstance(metadata, dict) else None
    if _INCIDENTAL_ID_PATTERN.search(logical_id):
        return True
    if cdk_path and _INCIDENTAL_PATH_PATTERN.search(str(cdk_path)):
        return True
    # User-configured patterns apply to both the logical ID and the cdk path.
    candidates = [logical_id] + ([str(cdk_path)] if cdk_path else [])
    for pattern in extra_patterns:
        for candidate in candidates:
            try:
                if re.search(pattern, candidate):
                    return True
            except re.error:
                continue
    return False


def _get_context(resource: dict[str, Any]) -> Any:
    """Return the resource's Context metadata block (any shape), or None."""
    metadata = resource.get("Metadata")
    if not isinstance(metadata, dict):
        return None
    return metadata.get(CONTEXT_KEY)


class ContextRuleMixin:
    """Shared config (extra incidental patterns) and iteration helpers."""

    config: dict[str, Any]
    id: str

    def __init__(self) -> None:
        super().__init__()
        # CloudFormationLintRule.__init__ resets config_definition to {} on the
        # instance, so the shared definition must be (re)applied here. cfn-lint's
        # rule registration then calls configure(), which applies these defaults
        # plus any user-provided --configure-rule overrides.
        #
        # Only additional_incidental_patterns is shared (all three rules use
        # _primary_resources). additional_low_value_types is I4010-only because
        # I4011/I4012 validate supplied context everywhere -- low-value resources
        # are not exempt from validation.
        self.config_definition = {
            "additional_incidental_patterns": dict(_PATTERNS_CONFIG),
        }
        self.config.setdefault("additional_incidental_patterns", [])

    @staticmethod
    def _is_cdk_template(cfn: Any) -> bool:
        """True when the template was synthesized by CDK (out of scope).

        Detected via the AWS::CDK::Metadata resource, the CDKMetadata logical
        ID, or any resource carrying aws:cdk:path (covers analyticsReporting off).
        """
        for logical_id, resource in cfn.get_resources().items():
            if (
                resource.get("Type") == _CDK_METADATA_TYPE
                or str(logical_id) == _CDK_METADATA_LOGICAL_ID
            ):
                return True
            metadata = resource.get("Metadata")
            if isinstance(metadata, dict) and _CDK_PATH_KEY in metadata:
                return True
        return False

    def _extra_patterns(self) -> list[str]:
        patterns = self.config.get("additional_incidental_patterns", [])
        return [str(p) for p in patterns] if isinstance(patterns, list) else []

    def _primary_resources(self, cfn: Any) -> list[tuple[str, dict[str, Any]]]:
        """Return (logical_id, resource) pairs for non-incidental resources."""
        extra = self._extra_patterns()
        results = []
        for logical_id, resource in cfn.get_resources().items():
            if _is_incidental(str(logical_id), resource, extra):
                continue
            results.append((str(logical_id), resource))
        return results
