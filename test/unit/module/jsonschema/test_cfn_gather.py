"""
Test cfnGather keyword functionality
"""

import pytest

from cfnlint.context import create_context_for_template
from cfnlint.jsonschema import CfnTemplateValidator
from cfnlint.jsonschema._keywords_cfn import _combine_gathered
from cfnlint.template import Template


@pytest.mark.parametrize(
    "constraint",
    [
        {"not": {"const": {"$data": "/remote/value"}}},
        {"if": {"const": {"$data": "/remote/value"}}, "then": False},
        {"oneOf": [{"const": {"$data": "/remote/value"}}, {"const": "actual"}]},
    ],
)
def test_unknown_gathered_value_in_composite_schema(constraint):
    schema = {
        "cfnGather": {
            "gather": {
                "local": {"properties": {"value": "/Value"}},
                "remote": {"reference": "/Target", "properties": {"value": "/Value"}},
            },
            "schema": {"properties": {"local": {"properties": {"value": constraint}}}},
        }
    }
    validator = CfnTemplateValidator(schema=schema, cfn=Template("", {}))
    assert list(validator.iter_errors({"Target": "external", "Value": "actual"})) == []


class TestCfnGather:
    """Test cfnGather keyword"""

    def test_basic_gather_with_data(self):
        """Test basic cfnGather with $data reference"""
        template = {
            "Resources": {
                "SourceQueue": {
                    "Type": "AWS::SQS::Queue",
                    "Properties": {
                        "FifoQueue": True,
                        "RedrivePolicy": {
                            "deadLetterTargetArn": {"Fn::GetAtt": ["DLQ", "Arn"]}
                        },
                    },
                },
                "DLQ": {
                    "Type": "AWS::SQS::Queue",
                    "Properties": {"FifoQueue": False},
                },
            }
        }

        schema = {
            "cfnGather": {
                "gather": {
                    "local": {
                        "properties": {
                            "FifoQueue": {"path": "/FifoQueue"},
                        }
                    },
                    "dlq": {
                        "reference": "/RedrivePolicy/deadLetterTargetArn",
                        "filter": {"type": "AWS::SQS::Queue"},
                        "properties": {
                            "FifoQueue": {"path": "/FifoQueue"},
                        },
                    },
                },
                "schema": {
                    "properties": {
                        "dlq": {
                            "properties": {
                                "FifoQueue": {"const": {"$data": "/local/FifoQueue"}}
                            }
                        }
                    }
                },
            }
        }

        cfn = Template("test.yaml", template)
        validator = CfnTemplateValidator(schema=schema, cfn=cfn)

        errors = list(
            validator.iter_errors(template["Resources"]["SourceQueue"]["Properties"])
        )

        assert len(errors) == 1
        assert "True was expected" in str(errors[0].message) or "const" in str(
            errors[0].message
        )

    def test_gather_matching_values(self):
        """Test cfnGather with matching values (no error)"""
        template = {
            "Resources": {
                "SourceQueue": {
                    "Type": "AWS::SQS::Queue",
                    "Properties": {
                        "FifoQueue": True,
                        "RedrivePolicy": {
                            "deadLetterTargetArn": {"Fn::GetAtt": ["DLQ", "Arn"]}
                        },
                    },
                },
                "DLQ": {
                    "Type": "AWS::SQS::Queue",
                    "Properties": {"FifoQueue": True},
                },
            }
        }

        schema = {
            "cfnGather": {
                "gather": {
                    "local": {
                        "properties": {
                            "FifoQueue": {"path": "/FifoQueue"},
                        }
                    },
                    "dlq": {
                        "reference": "/RedrivePolicy/deadLetterTargetArn",
                        "filter": {"type": "AWS::SQS::Queue"},
                        "properties": {
                            "FifoQueue": {"path": "/FifoQueue"},
                        },
                    },
                },
                "schema": {
                    "properties": {
                        "dlq": {
                            "properties": {
                                "FifoQueue": {"const": {"$data": "/local/FifoQueue"}}
                            }
                        }
                    }
                },
            }
        }

        cfn = Template("test.yaml", template)
        validator = CfnTemplateValidator(schema=schema, cfn=cfn)

        errors = list(
            validator.iter_errors(template["Resources"]["SourceQueue"]["Properties"])
        )

        assert len(errors) == 0

    def test_gather_with_type(self):
        """Test cfnGather including resource type via $type"""
        template = {
            "Resources": {
                "MyPermission": {
                    "Type": "AWS::Lambda::Permission",
                    "Properties": {"SourceArn": {"Fn::GetAtt": ["MyBucket", "Arn"]}},
                },
                "MyBucket": {"Type": "AWS::S3::Bucket", "Properties": {}},
            }
        }

        schema = {
            "cfnGather": {
                "gather": {
                    "target": {
                        "reference": "/SourceArn",
                        "properties": {
                            "type": "$type",
                        },
                    },
                },
                "schema": {
                    "properties": {
                        "target": {"properties": {"type": {"const": "AWS::S3::Bucket"}}}
                    }
                },
            }
        }

        cfn = Template("test.yaml", template)
        validator = CfnTemplateValidator(schema=schema, cfn=cfn)

        errors = list(
            validator.iter_errors(template["Resources"]["MyPermission"]["Properties"])
        )

        assert len(errors) == 0


class TestCombineGathered:
    """Direct tests for the _combine_gathered helper"""

    def _validator(self, template):
        cfn = Template("", template, regions=["us-east-1"])
        context = create_context_for_template(cfn)
        return CfnTemplateValidator(context=context, cfn=cfn)

    def test_no_keys_yields_empty_gathered(self):
        validator = self._validator({"Resources": {}})

        assert list(_combine_gathered(validator, {})) == [({}, validator)]
        assert list(_combine_gathered(validator, {"local": {}})) == [
            ({"local": {}}, validator)
        ]

    def test_unsatisfiable_combination_is_skipped(self):
        # C2 is the negation of C1, so pinning both true cannot happen
        # even though neither branch validator conflicts on its own
        template = {
            "Parameters": {
                "Mode": {"Type": "String", "AllowedValues": ["a", "b"]},
            },
            "Conditions": {
                "C1": {"Fn::Equals": [{"Ref": "Mode"}, "a"]},
                "C2": {"Fn::Not": [{"Condition": "C1"}]},
            },
            "Resources": {},
        }
        validator = self._validator(template)

        def branch(status):
            return validator.evolve(
                context=validator.context.evolve(
                    conditions=validator.context.conditions.evolve(status=status),
                ),
            )

        entries = {
            "local": {"value": [("x", branch({"C1": True}))]},
            "remote": {"value": [("y", branch({"C2": True}))]},
        }

        assert list(_combine_gathered(validator, entries)) == []


class TestGatherResolveReference:
    """Test cfnGather resolveReference canonicalization"""

    @pytest.mark.parametrize(
        "stage_rest_api,deployment_rest_api,expected_errors",
        [
            # Ref and GetAtt RestApiId name the same RestApi
            ({"Ref": "Api"}, {"Fn::GetAtt": ["Api", "RestApiId"]}, 0),
            # Reversed: GetAtt on the local side, Ref on the remote side
            ({"Fn::GetAtt": ["Api", "RestApiId"]}, {"Ref": "Api"}, 0),
            # GetAtt in string form is the same reference
            ({"Ref": "Api"}, {"Fn::GetAtt": "Api.RestApiId"}, 0),
            # GetAtt on a different attribute is not the RestApi id
            ({"Ref": "Api"}, {"Fn::GetAtt": ["Api", "RootResourceId"]}, 1),
            # GetAtt on a different RestApi is a mismatch
            ({"Ref": "Api"}, {"Fn::GetAtt": ["OtherApi", "RestApiId"]}, 1),
            # A literal value is left unchanged and still mismatches a Ref
            ({"Ref": "Api"}, "abc123", 1),
        ],
    )
    def test_gather_resolve_reference(
        self, stage_rest_api, deployment_rest_api, expected_errors
    ):
        """Test cfnGather resolveReference canonicalizes Ref/GetAtt pairs"""
        template = {
            "Resources": {
                "Api": {
                    "Type": "AWS::ApiGateway::RestApi",
                    "Properties": {"Name": "Api"},
                },
                "OtherApi": {
                    "Type": "AWS::ApiGateway::RestApi",
                    "Properties": {"Name": "OtherApi"},
                },
                "Deployment": {
                    "Type": "AWS::ApiGateway::Deployment",
                    "Properties": {"RestApiId": deployment_rest_api},
                },
                "Stage": {
                    "Type": "AWS::ApiGateway::Stage",
                    "Properties": {
                        "RestApiId": stage_rest_api,
                        "DeploymentId": {"Ref": "Deployment"},
                        "StageName": "test",
                    },
                },
            }
        }

        schema = {
            "cfnGather": {
                "gather": {
                    "deployment": {
                        "filter": {"type": "AWS::ApiGateway::Deployment"},
                        "properties": {
                            "RestApiId": {
                                "path": "/RestApiId",
                                "resolveReference": "RestApiId",
                            }
                        },
                        "reference": "/DeploymentId",
                    },
                    "stage": {
                        "properties": {
                            "RestApiId": {
                                "path": "/RestApiId",
                                "resolveReference": "RestApiId",
                            }
                        }
                    },
                },
                "schema": {
                    "cfnContext": {
                        "functions": [],
                        "schema": {
                            "properties": {
                                "deployment": {
                                    "properties": {
                                        "RestApiId": {
                                            "const": {"$data": "/stage/RestApiId"}
                                        }
                                    }
                                }
                            }
                        },
                    }
                },
            }
        }

        cfn = Template("test.yaml", template)
        validator = CfnTemplateValidator(schema=schema, cfn=cfn)

        errors = list(
            validator.iter_errors(template["Resources"]["Stage"]["Properties"])
        )

        assert len(errors) == expected_errors
