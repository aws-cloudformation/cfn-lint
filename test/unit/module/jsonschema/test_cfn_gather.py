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
