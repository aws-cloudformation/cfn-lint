"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from __future__ import annotations

from unittest.mock import patch

from cfnlint.context.context import Resource, _inject_sam_implicit_resources


class TestInjectSamImplicitResources:
    def test_non_dict_resources(self):
        resources: dict[str, Resource] = {}
        _inject_sam_implicit_resources("not-a-dict", resources)
        assert resources == {}

    def test_implicit_rest_api(self):
        template_resources = {
            "Fn": {
                "Type": "AWS::Serverless::Function",
                "Properties": {
                    "Events": {
                        "Api": {
                            "Type": "Api",
                            "Properties": {"Path": "/", "Method": "GET"},
                        }
                    }
                },
            }
        }
        resources: dict[str, Resource] = {}
        _inject_sam_implicit_resources(template_resources, resources)
        assert "ServerlessRestApi" in resources
        assert "FnRole" in resources

    def test_implicit_http_api(self):
        template_resources = {
            "Fn": {
                "Type": "AWS::Serverless::Function",
                "Properties": {
                    "Events": {
                        "Http": {
                            "Type": "HttpApi",
                            "Properties": {"Path": "/", "Method": "GET"},
                        }
                    }
                },
            }
        }
        resources: dict[str, Resource] = {}
        _inject_sam_implicit_resources(template_resources, resources)
        assert "ServerlessHttpApi" in resources

    def test_explicit_rest_api_id_no_implicit(self):
        template_resources = {
            "Fn": {
                "Type": "AWS::Serverless::Function",
                "Properties": {
                    "Events": {
                        "Api": {
                            "Type": "Api",
                            "Properties": {
                                "Path": "/",
                                "Method": "GET",
                                "RestApiId": {"Ref": "MyApi"},
                            },
                        }
                    }
                },
            }
        }
        resources: dict[str, Resource] = {}
        _inject_sam_implicit_resources(template_resources, resources)
        assert "ServerlessRestApi" not in resources

    def test_explicit_api_id_no_implicit_http(self):
        template_resources = {
            "Fn": {
                "Type": "AWS::Serverless::Function",
                "Properties": {
                    "Events": {
                        "Http": {
                            "Type": "HttpApi",
                            "Properties": {
                                "Path": "/",
                                "Method": "GET",
                                "ApiId": {"Ref": "MyApi"},
                            },
                        }
                    }
                },
            }
        }
        resources: dict[str, Resource] = {}
        _inject_sam_implicit_resources(template_resources, resources)
        assert "ServerlessHttpApi" not in resources

    def test_role_generation(self):
        template_resources = {
            "Fn": {
                "Type": "AWS::Serverless::Function",
                "Properties": {},
            }
        }
        resources: dict[str, Resource] = {}
        _inject_sam_implicit_resources(template_resources, resources)
        assert "FnRole" in resources

    def test_no_role_when_explicit(self):
        template_resources = {
            "Fn": {
                "Type": "AWS::Serverless::Function",
                "Properties": {"Role": "arn:aws:iam::123456789012:role/role"},
            }
        }
        resources: dict[str, Resource] = {}
        _inject_sam_implicit_resources(template_resources, resources)
        assert "FnRole" not in resources

    def test_state_machine_role(self):
        template_resources = {
            "SM": {
                "Type": "AWS::Serverless::StateMachine",
                "Properties": {},
            }
        }
        resources: dict[str, Resource] = {}
        _inject_sam_implicit_resources(template_resources, resources)
        assert "SMRole" in resources

    def test_version_alias_with_auto_publish(self):
        template_resources = {
            "Fn": {
                "Type": "AWS::Serverless::Function",
                "Properties": {"AutoPublishAlias": "live"},
            }
        }
        resources: dict[str, Resource] = {}
        _inject_sam_implicit_resources(template_resources, resources)
        assert "Fn.Version" in resources
        assert "Fn.Alias" in resources

    def test_version_alias_with_deployment_preference(self):
        template_resources = {
            "Fn": {
                "Type": "AWS::Serverless::Function",
                "Properties": {"DeploymentPreference": {"Type": "AllAtOnce"}},
            }
        }
        resources: dict[str, Resource] = {}
        _inject_sam_implicit_resources(template_resources, resources)
        assert "Fn.Version" in resources
        assert "Fn.Alias" in resources

    def test_no_version_alias_without_publish(self):
        template_resources = {
            "Fn": {
                "Type": "AWS::Serverless::Function",
                "Properties": {"Handler": "index.handler"},
            }
        }
        resources: dict[str, Resource] = {}
        _inject_sam_implicit_resources(template_resources, resources)
        assert "Fn.Version" not in resources
        assert "Fn.Alias" not in resources

    def test_non_dict_resource_skipped(self):
        template_resources = {"Bad": "not-a-dict"}
        resources: dict[str, Resource] = {}
        _inject_sam_implicit_resources(template_resources, resources)
        assert resources == {}

    def test_non_dict_events_skipped(self):
        template_resources = {
            "Fn": {
                "Type": "AWS::Serverless::Function",
                "Properties": {"Events": "not-a-dict"},
            }
        }
        resources: dict[str, Resource] = {}
        _inject_sam_implicit_resources(template_resources, resources)
        assert "ServerlessRestApi" not in resources

    def test_non_dict_event_skipped(self):
        template_resources = {
            "Fn": {
                "Type": "AWS::Serverless::Function",
                "Properties": {"Events": {"Bad": "not-a-dict"}},
            }
        }
        resources: dict[str, Resource] = {}
        _inject_sam_implicit_resources(template_resources, resources)
        assert "ServerlessRestApi" not in resources

    def test_non_dict_props_treated_as_empty(self):
        template_resources = {
            "Fn": {
                "Type": "AWS::Serverless::Function",
                "Properties": "not-a-dict",
            }
        }
        resources: dict[str, Resource] = {}
        _inject_sam_implicit_resources(template_resources, resources)
        assert "FnRole" in resources

    @patch("cfnlint.context.context.Resource", side_effect=ValueError("mocked error"))
    def test_role_value_error_is_caught(self, mock_resource):
        template_resources = {
            "Fn": {
                "Type": "AWS::Serverless::Function",
                "Properties": {},
            }
        }
        resources: dict[str, Resource] = {}
        _inject_sam_implicit_resources(template_resources, resources)
        assert "FnRole" not in resources

    @patch("cfnlint.context.context.Resource", side_effect=ValueError("mocked error"))
    def test_version_alias_value_error_is_caught(self, mock_resource):
        template_resources = {
            "Fn": {
                "Type": "AWS::Serverless::Function",
                "Properties": {"AutoPublishAlias": "live"},
            }
        }
        resources: dict[str, Resource] = {}
        _inject_sam_implicit_resources(template_resources, resources)
        assert "Fn.Version" not in resources
        assert "Fn.Alias" not in resources

    @patch("cfnlint.context.context.Resource", side_effect=ValueError("mocked error"))
    def test_implicit_rest_api_value_error_is_caught(self, mock_resource):
        template_resources = {
            "Fn": {
                "Type": "AWS::Serverless::Function",
                "Properties": {
                    "Events": {
                        "Api": {
                            "Type": "Api",
                            "Properties": {"Path": "/", "Method": "GET"},
                        }
                    }
                },
            }
        }
        resources: dict[str, Resource] = {}
        _inject_sam_implicit_resources(template_resources, resources)
        assert "ServerlessRestApi" not in resources

    @patch("cfnlint.context.context.Resource", side_effect=ValueError("mocked error"))
    def test_implicit_http_api_value_error_is_caught(self, mock_resource):
        template_resources = {
            "Fn": {
                "Type": "AWS::Serverless::Function",
                "Properties": {
                    "Events": {
                        "Http": {
                            "Type": "HttpApi",
                            "Properties": {"Path": "/", "Method": "GET"},
                        }
                    }
                },
            }
        }
        resources: dict[str, Resource] = {}
        _inject_sam_implicit_resources(template_resources, resources)
        assert "ServerlessHttpApi" not in resources

    def test_non_serverless_resource_skipped(self):
        """Cover branch where resource_type is not in the SAM types tuple."""
        template_resources = {
            "Bucket": {
                "Type": "AWS::S3::Bucket",
                "Properties": {},
            }
        }
        resources: dict[str, Resource] = {}
        _inject_sam_implicit_resources(template_resources, resources)
        assert resources == {}

    def test_version_already_exists_not_overwritten(self):
        """Cover branch where version_id is already in resources."""
        template_resources = {
            "Fn": {
                "Type": "AWS::Serverless::Function",
                "Properties": {"AutoPublishAlias": "live"},
            }
        }
        existing = Resource({"Type": "AWS::Lambda::Version"})
        resources: dict[str, Resource] = {"Fn.Version": existing, "Fn.Alias": existing}
        _inject_sam_implicit_resources(template_resources, resources)
        assert resources["Fn.Version"] is existing
        assert resources["Fn.Alias"] is existing

    def test_empty_events_dict(self):
        """Cover branch where events.values() loop body is never entered."""
        template_resources = {
            "Fn": {
                "Type": "AWS::Serverless::Function",
                "Properties": {"Events": {}},
            }
        }
        resources: dict[str, Resource] = {}
        _inject_sam_implicit_resources(template_resources, resources)
        assert "ServerlessRestApi" not in resources
        assert "ServerlessHttpApi" not in resources

    def test_non_api_event_type_skipped(self):
        """Cover branch where event type is neither Api nor HttpApi."""
        template_resources = {
            "Fn": {
                "Type": "AWS::Serverless::Function",
                "Properties": {
                    "Events": {
                        "Sqs": {
                            "Type": "SQS",
                            "Properties": {"Queue": "arn:aws:sqs:us-east-1:1:q"},
                        }
                    }
                },
            }
        }
        resources: dict[str, Resource] = {}
        _inject_sam_implicit_resources(template_resources, resources)
        assert "ServerlessRestApi" not in resources
        assert "ServerlessHttpApi" not in resources

    def test_function_url_config(self):
        """FunctionUrlConfig generates a Url resource."""
        template_resources = {
            "Fn": {
                "Type": "AWS::Serverless::Function",
                "Properties": {"FunctionUrlConfig": {"AuthType": "NONE"}},
            }
        }
        resources: dict[str, Resource] = {}
        _inject_sam_implicit_resources(template_resources, resources)
        assert "FnUrl" in resources
        assert resources["FnUrl"].type == "AWS::Lambda::Url"

    def test_deployment_preference_codedeploy(self):
        """DeploymentPreference generates CodeDeploy resources."""
        template_resources = {
            "Fn": {
                "Type": "AWS::Serverless::Function",
                "Properties": {
                    "DeploymentPreference": {"Type": "Linear10PercentEvery10Minutes"}
                },
            }
        }
        resources: dict[str, Resource] = {}
        _inject_sam_implicit_resources(template_resources, resources)
        assert "ServerlessDeploymentApplication" in resources
        assert "FnDeploymentGroup" in resources
        assert "CodeDeployServiceRole" in resources

    def test_deployment_preference_explicit_role(self):
        """DeploymentPreference with explicit Role skips CodeDeployServiceRole."""
        template_resources = {
            "Fn": {
                "Type": "AWS::Serverless::Function",
                "Properties": {
                    "DeploymentPreference": {
                        "Type": "AllAtOnce",
                        "Role": "arn:aws:iam::123456789012:role/my-role",
                    }
                },
            }
        }
        resources: dict[str, Resource] = {}
        _inject_sam_implicit_resources(template_resources, resources)
        assert "ServerlessDeploymentApplication" in resources
        assert "FnDeploymentGroup" in resources
        assert "CodeDeployServiceRole" not in resources

    def test_deployment_preference_disabled(self):
        """DeploymentPreference with Enabled: false generates nothing."""
        template_resources = {
            "Fn": {
                "Type": "AWS::Serverless::Function",
                "Properties": {"DeploymentPreference": {"Enabled": False}},
            }
        }
        resources: dict[str, Resource] = {}
        _inject_sam_implicit_resources(template_resources, resources)
        assert "ServerlessDeploymentApplication" not in resources
        assert "FnDeploymentGroup" not in resources

    def test_event_permissions(self):
        """Each event generates a Permission resource."""
        template_resources = {
            "Fn": {
                "Type": "AWS::Serverless::Function",
                "Properties": {
                    "Events": {
                        "MyApi": {
                            "Type": "Api",
                            "Properties": {
                                "Path": "/",
                                "Method": "GET",
                                "RestApiId": "x",
                            },
                        },
                        "MySchedule": {
                            "Type": "Schedule",
                            "Properties": {"Schedule": "rate(1 hour)"},
                        },
                    }
                },
            }
        }
        resources: dict[str, Resource] = {}
        _inject_sam_implicit_resources(template_resources, resources)
        assert "FnMyApiPermission" in resources
        assert "FnMySchedulePermission" in resources

    def test_api_stage(self):
        """Api always generates a Stage resource."""
        template_resources = {
            "MyApi": {
                "Type": "AWS::Serverless::Api",
                "Properties": {"StageName": "prod"},
            }
        }
        resources: dict[str, Resource] = {}
        _inject_sam_implicit_resources(template_resources, resources)
        assert "MyApiStage" in resources
        assert resources["MyApiStage"].type == "AWS::ApiGateway::Stage"

    def test_api_domain_and_usage_plan(self):
        """Api with Domain and Auth generates DomainName and UsagePlan."""
        template_resources = {
            "MyApi": {
                "Type": "AWS::Serverless::Api",
                "Properties": {
                    "StageName": "prod",
                    "Domain": {"DomainName": "api.example.com"},
                    "Auth": {"ApiKeyRequired": True},
                },
            }
        }
        resources: dict[str, Resource] = {}
        _inject_sam_implicit_resources(template_resources, resources)
        assert "MyApiDomainName" in resources
        assert "MyApiUsagePlan" in resources

    def test_http_api_stage(self):
        """HttpApi always generates a Stage resource."""
        template_resources = {
            "MyHttpApi": {
                "Type": "AWS::Serverless::HttpApi",
                "Properties": {"StageName": "prod"},
            }
        }
        resources: dict[str, Resource] = {}
        _inject_sam_implicit_resources(template_resources, resources)
        assert "MyHttpApiStage" in resources
        assert resources["MyHttpApiStage"].type == "AWS::ApiGatewayV2::Stage"

    def test_implicit_api_stages(self):
        """Implicit APIs also get Stage resources."""
        template_resources = {
            "Fn": {
                "Type": "AWS::Serverless::Function",
                "Properties": {
                    "Events": {
                        "A": {
                            "Type": "Api",
                            "Properties": {"Path": "/", "Method": "GET"},
                        },
                        "B": {
                            "Type": "HttpApi",
                            "Properties": {"Path": "/", "Method": "GET"},
                        },
                    }
                },
            }
        }
        resources: dict[str, Resource] = {}
        _inject_sam_implicit_resources(template_resources, resources)
        assert "ServerlessRestApi" in resources
        assert "ServerlessRestApiStage" in resources
        assert "ServerlessHttpApi" in resources
        assert "ServerlessHttpApiStage" in resources
