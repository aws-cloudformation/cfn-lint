"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from typing import Any, Iterator

from cfnlint._typing import Path, RuleMatches
from cfnlint.helpers import PSEUDOPARAMS, REGEX_SUB_PARAMETERS
from cfnlint.rules import CloudFormationLintRule, RuleMatch
from cfnlint.template import Template

_LAMBDA_TYPES = frozenset(
    [
        "AWS::Lambda::Function",
        "AWS::Lambda::Alias",
        "AWS::Lambda::Version",
        "AWS::Serverless::Function",
    ]
)

# SAM adds a Lambda permission for these function event types
_SAM_EVENT_PRINCIPALS = {
    "Api": "apigateway.amazonaws.com",
    "HttpApi": "apigateway.amazonaws.com",
    "S3": "s3.amazonaws.com",
    "CloudWatchEvent": "events.amazonaws.com",
    "EventBridgeRule": "events.amazonaws.com",
    "Schedule": "events.amazonaws.com",
}

# Sentinel for a reference that can't be resolved to a template resource
_UNKNOWN = object()


class ConnectedResourcePermissions(CloudFormationLintRule):
    """Check that resource policies exist when resources are connected"""

    id = "W3706"
    shortdesc = "Validate resource policies exist for connected resources"
    description = (
        "When a resource is configured to invoke or send to another resource "
        "in the template, the target needs a resource policy that allows the "
        "calling service. Checks Lambda functions invoked by API Gateway, S3 "
        "and EventBridge, SQS queues and SNS topics used as S3 notification "
        "destinations"
    )
    source_url = "https://github.com/aws-cloudformation/cfn-lint/issues/2268"
    tags = ["resources", "iam", "lambda", "sqs", "sns", "s3", "apigateway"]

    def match(self, cfn: Template) -> RuleMatches:
        matches: RuleMatches = []

        resources = cfn.get_resources()
        lambda_grants = self._lambda_grants(cfn)
        queue_grants = self._policy_grants(
            cfn, "AWS::SQS::QueuePolicy", "Queues", "PolicyDocument"
        )
        topic_grants = self._policy_grants(
            cfn, "AWS::SNS::TopicPolicy", "Topics", "PolicyDocument"
        )
        for target, principals in self._policy_grants(
            cfn, "AWS::SNS::TopicInlinePolicy", "TopicArn", "PolicyDocument"
        ).items():
            topic_grants.setdefault(target, set()).update(principals)

        for path, target, service in self._connections(cfn):
            target_type = resources.get(target, {}).get("Type")
            if target_type in _LAMBDA_TYPES:
                grants, policy_type = lambda_grants, "AWS::Lambda::Permission"
            elif target_type == "AWS::SQS::Queue":
                grants, policy_type = queue_grants, "AWS::SQS::QueuePolicy"
            elif target_type == "AWS::SNS::Topic":
                grants, policy_type = (
                    topic_grants,
                    "AWS::SNS::TopicPolicy or AWS::SNS::TopicInlinePolicy",
                )
            else:
                continue

            # A permission on "Function:alias" resolves to the function, so a
            # grant on the function is accepted for its aliases and versions
            keys = [target]
            if target_type in ("AWS::Lambda::Alias", "AWS::Lambda::Version"):
                keys.extend(
                    self._targets(
                        self._get(resources[target], "Properties", "FunctionName")
                    )
                )
            if any(self._is_granted(grants, key, service) for key in keys):
                continue

            matches.append(
                RuleMatch(
                    path,
                    (
                        f"{target_type} {target!r} is connected to {service!r} "
                        f"but no {policy_type} in the template allows "
                        f"{service!r} to access it"
                    ),
                )
            )

        return matches

    @staticmethod
    def _is_granted(grants: dict[Any, set[Any]], target: str, service: str) -> bool:
        for key in (target, _UNKNOWN):
            principals = grants.get(key, set())
            if service in principals or "*" in principals or _UNKNOWN in principals:
                return True
        return False

    # Grants
    def _lambda_grants(self, cfn: Template) -> dict[Any, set[Any]]:
        grants: dict[Any, set[Any]] = {}
        for _, resource in cfn.get_resources(["AWS::Lambda::Permission"]).items():
            properties = resource.get("Properties")
            if not isinstance(properties, dict):
                grants.setdefault(_UNKNOWN, set()).add(_UNKNOWN)
                continue
            principal = properties.get("Principal")
            principal = principal if isinstance(principal, str) else _UNKNOWN
            for target in self._resource_targets(cfn, properties.get("FunctionName")):
                grants.setdefault(target, set()).add(principal)

        for name, resource in cfn.get_resources(["AWS::Serverless::Function"]).items():
            events = self._get(resource, "Properties", "Events")
            if not isinstance(events, dict):
                continue
            for event in events.values():
                event_type = event.get("Type") if isinstance(event, dict) else None
                if not isinstance(event_type, str):
                    grants.setdefault(name, set()).add(_UNKNOWN)
                elif event_type in _SAM_EVENT_PRINCIPALS:
                    grants.setdefault(name, set()).add(
                        _SAM_EVENT_PRINCIPALS[event_type]
                    )
        return grants

    def _policy_grants(
        self, cfn: Template, resource_type: str, targets_key: str, document_key: str
    ) -> dict[Any, set[Any]]:
        grants: dict[Any, set[Any]] = {}
        for _, resource in cfn.get_resources([resource_type]).items():
            properties = resource.get("Properties")
            if not isinstance(properties, dict):
                grants.setdefault(_UNKNOWN, set()).add(_UNKNOWN)
                continue
            principals = self._service_principals(properties.get(document_key))
            values = properties.get(targets_key)
            if not isinstance(values, list):
                values = [values]
            for value in values:
                for target in self._resource_targets(cfn, value):
                    grants.setdefault(target, set()).update(principals)
        return grants

    def _service_principals(self, document: Any) -> set[Any]:
        """Principals allowed by a policy document. Anything that can't be
        read is reported as unknown so it is treated as a grant."""
        if not isinstance(document, dict):
            return {_UNKNOWN}
        statements = document.get("Statement")
        if isinstance(statements, dict):
            statements = [statements]
        if not isinstance(statements, list):
            return {_UNKNOWN}

        principals: set[Any] = set()
        for statement in statements:
            if not isinstance(statement, dict):
                principals.add(_UNKNOWN)
                continue
            effect = statement.get("Effect")
            if not isinstance(effect, str):
                principals.add(_UNKNOWN)
                continue
            if effect != "Allow":
                continue
            principal = statement.get("Principal")
            if principal == "*":
                principals.add("*")
                continue
            if not isinstance(principal, dict):
                principals.add(_UNKNOWN)
                continue
            for key, value in principal.items():
                if key == "AWS" and value == "*":
                    principals.add("*")
                elif key == "Service":
                    for service in value if isinstance(value, list) else [value]:
                        principals.add(
                            service if isinstance(service, str) else _UNKNOWN
                        )
                elif key not in ("AWS", "Federated", "CanonicalUser"):
                    principals.add(_UNKNOWN)
        return principals

    # Connections
    def _connections(self, cfn: Template) -> Iterator[tuple[Path, Any, str]]:
        """Yield (path, target resource, calling service principal)"""
        lambdas = cfn.get_resources(list(_LAMBDA_TYPES))
        for name, resource in cfn.get_resources(["AWS::ApiGateway::Method"]).items():
            integration = self._get(resource, "Properties", "Integration")
            if not isinstance(integration, dict):
                continue
            if integration.get("Type") not in ("AWS", "AWS_PROXY"):
                continue
            if "Credentials" in integration:
                continue
            path: Path = ["Resources", name, "Properties", "Integration", "Uri"]
            for target in self._targets(integration.get("Uri")):
                if target is not _UNKNOWN:
                    yield path, target, "apigateway.amazonaws.com"

        for name, resource in cfn.get_resources(
            ["AWS::ApiGatewayV2::Integration"]
        ).items():
            properties = self._get(resource, "Properties")
            if not isinstance(properties, dict):
                continue
            if properties.get("IntegrationType") not in ("AWS", "AWS_PROXY"):
                continue
            if "CredentialsArn" in properties:
                continue
            path = ["Resources", name, "Properties", "IntegrationUri"]
            for target in self._targets(properties.get("IntegrationUri")):
                if target is not _UNKNOWN:
                    yield path, target, "apigateway.amazonaws.com"

        # HTTP API quick create
        for name, resource in cfn.get_resources(["AWS::ApiGatewayV2::Api"]).items():
            properties = self._get(resource, "Properties")
            if not isinstance(properties, dict) or "CredentialsArn" in properties:
                continue
            path = ["Resources", name, "Properties", "Target"]
            for target in self._targets(properties.get("Target")):
                if target is not _UNKNOWN:
                    yield path, target, "apigateway.amazonaws.com"

        for resource_type, body_key in (
            ("AWS::ApiGateway::RestApi", "Body"),
            ("AWS::ApiGatewayV2::Api", "Body"),
            ("AWS::Serverless::Api", "DefinitionBody"),
            ("AWS::Serverless::HttpApi", "DefinitionBody"),
        ):
            for name, resource in cfn.get_resources([resource_type]).items():
                body = self._get(resource, "Properties", body_key)
                for path, integration in self._openapi_integrations(
                    body, ["Resources", name, "Properties", body_key]
                ):
                    if str(integration.get("type")).lower() not in ("aws", "aws_proxy"):
                        continue
                    if "credentials" in integration:
                        continue
                    for target in self._targets(integration.get("uri")):
                        if target is not _UNKNOWN:
                            yield path + ["uri"], target, "apigateway.amazonaws.com"

        for name, resource in cfn.get_resources(["AWS::S3::Bucket"]).items():
            notifications = self._get(
                resource, "Properties", "NotificationConfiguration"
            )
            if not isinstance(notifications, dict):
                continue
            for config_key, target_key in (
                ("LambdaConfigurations", "Function"),
                ("QueueConfigurations", "Queue"),
                ("TopicConfigurations", "Topic"),
            ):
                configs = notifications.get(config_key)
                if not isinstance(configs, list):
                    continue
                for i, config in enumerate(configs):
                    if not isinstance(config, dict):
                        continue
                    path = [
                        "Resources",
                        name,
                        "Properties",
                        "NotificationConfiguration",
                        config_key,
                        i,
                        target_key,
                    ]
                    for target in self._targets(config.get(target_key)):
                        if target is not _UNKNOWN:
                            yield path, target, "s3.amazonaws.com"

        for name, resource in cfn.get_resources(["AWS::Events::Rule"]).items():
            targets = self._get(resource, "Properties", "Targets")
            if not isinstance(targets, list):
                continue
            for i, event_target in enumerate(targets):
                if not isinstance(event_target, dict):
                    continue
                path = ["Resources", name, "Properties", "Targets", i, "Arn"]
                for target in self._targets(event_target.get("Arn")):
                    # SQS and SNS targets can be allowed through a role or a
                    # resource policy, so only Lambda targets are checked
                    if target is not _UNKNOWN and lambdas.get(target) is not None:
                        yield path, target, "events.amazonaws.com"

    def _openapi_integrations(
        self, value: Any, path: Path
    ) -> Iterator[tuple[Path, dict[str, Any]]]:
        """Yield the x-amazon-apigateway-integration objects in an OpenAPI
        definition"""
        if isinstance(value, dict):
            for key, item in value.items():
                if key == "x-amazon-apigateway-integration" and isinstance(item, dict):
                    yield [*path, key], item
                elif key not in ("Fn::Transform", "Fn::Sub", "Fn::GetAtt", "Ref"):
                    yield from self._openapi_integrations(item, [*path, key])
        elif isinstance(value, list):
            for i, item in enumerate(value):
                yield from self._openapi_integrations(item, [*path, i])

    @staticmethod
    def _get(obj: Any, *keys: str) -> Any:
        for key in keys:
            if not isinstance(obj, dict):
                return None
            obj = obj.get(key)
        return obj

    def _resource_targets(self, cfn: Template, value: Any) -> Iterator[Any]:
        """Like _targets, but a reference to anything other than a resource,
        such as a parameter, is unknown"""
        resources = cfn.get_resources()
        for target in self._targets(value):
            yield target if target in resources else _UNKNOWN

    def _targets(self, value: Any) -> Iterator[Any]:
        """Yield the logical IDs of template resources a value refers to.
        Yields _UNKNOWN when the value can't be fully resolved."""
        if isinstance(value, str):
            return
        if not isinstance(value, dict) or len(value) != 1:
            yield _UNKNOWN
            return

        key, arg = next(iter(value.items()))
        if key == "Ref":
            if isinstance(arg, str) and arg not in PSEUDOPARAMS:
                yield arg
            else:
                yield _UNKNOWN
        elif key == "Fn::GetAtt":
            if isinstance(arg, list) and arg and isinstance(arg[0], str):
                yield arg[0]
            elif isinstance(arg, str):
                yield arg.split(".", 1)[0]
            else:
                yield _UNKNOWN
        elif key == "Fn::Sub":
            variables: dict[str, Any] = {}
            if isinstance(arg, list) and len(arg) == 2:
                arg, variables = arg
                if not isinstance(variables, dict):
                    variables = {}
            if not isinstance(arg, str):
                yield _UNKNOWN
                return
            for parameter in REGEX_SUB_PARAMETERS.findall(arg):
                if parameter in variables:
                    yield from self._targets(variables[parameter])
                elif parameter not in PSEUDOPARAMS:
                    yield parameter.split(".", 1)[0]
        elif key == "Fn::Join":
            if isinstance(arg, list) and len(arg) == 2 and isinstance(arg[1], list):
                for item in arg[1]:
                    yield from self._targets(item)
            else:
                yield _UNKNOWN
        elif key == "Fn::If":
            if isinstance(arg, list) and len(arg) == 3:
                yield from self._targets(arg[1])
                yield from self._targets(arg[2])
            else:
                yield _UNKNOWN
        else:
            yield _UNKNOWN
