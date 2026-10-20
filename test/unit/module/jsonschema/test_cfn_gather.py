"""
Test cfnGather keyword functionality
"""

import pytest

from cfnlint.jsonschema import CfnTemplateValidator
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
