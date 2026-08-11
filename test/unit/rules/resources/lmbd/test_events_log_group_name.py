"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

from test.unit.rules import BaseRuleTestCase

import pytest

from cfnlint.rules.resources.lmbd.EventsLogGroupName import EventsLogGroupName
from cfnlint.template import Template


class TestEventsLogGroupName(BaseRuleTestCase):
    """Test Lambda Trigger Events CloudWatchLogs Property Configuration"""

    def setUp(self):
        """Setup"""
        super(TestEventsLogGroupName, self).setUp()
        self.collection.register(EventsLogGroupName())
        self.success_templates = [
            "test/fixtures/templates/good/some_logs_stream_lambda.yaml"
        ]

    def test_file_positive(self):
        """Test Positive"""
        self.helper_file_positive()

    def test_file_negative(self):
        """Test failure"""
        # The bad fixture has 3 CloudWatchLogs events pointing to FunctionALogGroup
        # which exceeds the limit of 2
        self.helper_file_negative(
            "test/fixtures/templates/bad/some_logs_stream_lambda.yaml",
            1,
        )


@pytest.fixture(scope="module")
def rule():
    return EventsLogGroupName()


class TestEventsLogGroupNameUnit:
    """Unit tests for E2529 rule"""

    def test_sam_events_exceeds_limit(self, rule):
        """Test that >2 SAM CloudWatchLogs events on one log group fails"""
        template = Template(
            "",
            {
                "AWSTemplateFormatVersion": "2010-09-09",
                "Transform": "AWS::Serverless-2016-10-31",
                "Resources": {
                    "MyLogGroup": {
                        "Type": "AWS::Logs::LogGroup",
                        "Properties": {"LogGroupName": "/aws/lambda/my-function"},
                    },
                    "LogSubscriptionFunction": {
                        "Type": "AWS::Serverless::Function",
                        "Properties": {
                            "CodeUri": "hello_world/",
                            "Handler": "app.lambda_handler",
                            "Runtime": "python3.9",
                            "Events": {
                                "Event1": {
                                    "Type": "CloudWatchLogs",
                                    "Properties": {
                                        "LogGroupName": {"Ref": "MyLogGroup"},
                                        "FilterPattern": "",
                                    },
                                },
                                "Event2": {
                                    "Type": "CloudWatchLogs",
                                    "Properties": {
                                        "LogGroupName": {"Ref": "MyLogGroup"},
                                        "FilterPattern": "",
                                    },
                                },
                                "Event3": {
                                    "Type": "CloudWatchLogs",
                                    "Properties": {
                                        "LogGroupName": {"Ref": "MyLogGroup"},
                                        "FilterPattern": "",
                                    },
                                },
                            },
                        },
                    },
                },
            },
        )
        matches = rule.match(template)
        assert len(matches) == 1
        # Verify path points to the SAM function's event
        assert matches[0].path[0] == "Resources"
        assert matches[0].path[1] == "LogSubscriptionFunction"
        assert matches[0].path[3] == "Events"

    def test_sam_events_within_limit(self, rule):
        """Test that <=2 SAM CloudWatchLogs events on one log group passes"""
        template = Template(
            "",
            {
                "AWSTemplateFormatVersion": "2010-09-09",
                "Transform": "AWS::Serverless-2016-10-31",
                "Resources": {
                    "MyLogGroup": {
                        "Type": "AWS::Logs::LogGroup",
                        "Properties": {"LogGroupName": "/aws/lambda/my-function"},
                    },
                    "LogSubscriptionFunction": {
                        "Type": "AWS::Serverless::Function",
                        "Properties": {
                            "CodeUri": "hello_world/",
                            "Handler": "app.lambda_handler",
                            "Runtime": "python3.9",
                            "Events": {
                                "Event1": {
                                    "Type": "CloudWatchLogs",
                                    "Properties": {
                                        "LogGroupName": {"Ref": "MyLogGroup"},
                                        "FilterPattern": "",
                                    },
                                },
                                "Event2": {
                                    "Type": "CloudWatchLogs",
                                    "Properties": {
                                        "LogGroupName": {"Ref": "MyLogGroup"},
                                        "FilterPattern": "",
                                    },
                                },
                            },
                        },
                    },
                },
            },
        )
        matches = rule.match(template)
        assert len(matches) == 0

    def test_sam_events_unique_log_groups(self, rule):
        """Test that SAM events on unique log groups passes"""
        template = Template(
            "",
            {
                "AWSTemplateFormatVersion": "2010-09-09",
                "Transform": "AWS::Serverless-2016-10-31",
                "Resources": {
                    "LogGroup1": {
                        "Type": "AWS::Logs::LogGroup",
                        "Properties": {"LogGroupName": "/aws/lambda/function1"},
                    },
                    "LogGroup2": {
                        "Type": "AWS::Logs::LogGroup",
                        "Properties": {"LogGroupName": "/aws/lambda/function2"},
                    },
                    "LogGroup3": {
                        "Type": "AWS::Logs::LogGroup",
                        "Properties": {"LogGroupName": "/aws/lambda/function3"},
                    },
                    "LogSubscriptionFunction": {
                        "Type": "AWS::Serverless::Function",
                        "Properties": {
                            "CodeUri": "hello_world/",
                            "Handler": "app.lambda_handler",
                            "Runtime": "python3.9",
                            "Events": {
                                "Event1": {
                                    "Type": "CloudWatchLogs",
                                    "Properties": {
                                        "LogGroupName": {"Ref": "LogGroup1"},
                                        "FilterPattern": "",
                                    },
                                },
                                "Event2": {
                                    "Type": "CloudWatchLogs",
                                    "Properties": {
                                        "LogGroupName": {"Ref": "LogGroup2"},
                                        "FilterPattern": "",
                                    },
                                },
                                "Event3": {
                                    "Type": "CloudWatchLogs",
                                    "Properties": {
                                        "LogGroupName": {"Ref": "LogGroup3"},
                                        "FilterPattern": "",
                                    },
                                },
                            },
                        },
                    },
                },
            },
        )
        matches = rule.match(template)
        assert len(matches) == 0

    def test_mixed_explicit_filter_and_sam_events(self, rule):
        """Test mixed explicit SubscriptionFilter and SAM events exceeding limit"""
        dest_arn = "arn:aws:lambda:us-east-1:123456789012:function:f"
        template = Template(
            "",
            {
                "AWSTemplateFormatVersion": "2010-09-09",
                "Transform": "AWS::Serverless-2016-10-31",
                "Resources": {
                    "MyLogGroup": {
                        "Type": "AWS::Logs::LogGroup",
                        "Properties": {"LogGroupName": "/aws/lambda/my-function"},
                    },
                    "ExplicitFilter1": {
                        "Type": "AWS::Logs::SubscriptionFilter",
                        "Properties": {
                            "LogGroupName": {"Ref": "MyLogGroup"},
                            "FilterPattern": "",
                            "DestinationArn": dest_arn,
                        },
                    },
                    "ExplicitFilter2": {
                        "Type": "AWS::Logs::SubscriptionFilter",
                        "Properties": {
                            "LogGroupName": {"Ref": "MyLogGroup"},
                            "FilterPattern": "",
                            "DestinationArn": dest_arn,
                        },
                    },
                    "LogSubscriptionFunction": {
                        "Type": "AWS::Serverless::Function",
                        "Properties": {
                            "CodeUri": "hello_world/",
                            "Handler": "app.lambda_handler",
                            "Runtime": "python3.9",
                            "Events": {
                                "Event1": {
                                    "Type": "CloudWatchLogs",
                                    "Properties": {
                                        "LogGroupName": {"Ref": "MyLogGroup"},
                                        "FilterPattern": "",
                                    },
                                },
                            },
                        },
                    },
                },
            },
        )
        # 2 explicit filters + 1 SAM event = 3, exceeds limit of 2
        matches = rule.match(template)
        assert len(matches) == 1

    def test_explicit_filters_only_exceeds_limit(self, rule):
        """Test explicit SubscriptionFilters exceeding limit"""
        dest_arn = "arn:aws:lambda:us-east-1:123456789012:function:f"
        template = Template(
            "",
            {
                "AWSTemplateFormatVersion": "2010-09-09",
                "Resources": {
                    "MyLogGroup": {
                        "Type": "AWS::Logs::LogGroup",
                        "Properties": {"LogGroupName": "/aws/lambda/my-function"},
                    },
                    "ExplicitFilter1": {
                        "Type": "AWS::Logs::SubscriptionFilter",
                        "Properties": {
                            "LogGroupName": {"Ref": "MyLogGroup"},
                            "FilterPattern": "",
                            "DestinationArn": dest_arn,
                        },
                    },
                    "ExplicitFilter2": {
                        "Type": "AWS::Logs::SubscriptionFilter",
                        "Properties": {
                            "LogGroupName": {"Ref": "MyLogGroup"},
                            "FilterPattern": "",
                            "DestinationArn": dest_arn,
                        },
                    },
                    "ExplicitFilter3": {
                        "Type": "AWS::Logs::SubscriptionFilter",
                        "Properties": {
                            "LogGroupName": {"Ref": "MyLogGroup"},
                            "FilterPattern": "",
                            "DestinationArn": dest_arn,
                        },
                    },
                },
            },
        )
        matches = rule.match(template)
        assert len(matches) == 1

    def test_non_cloudwatchlogs_event_ignored(self, rule):
        """Test that non-CloudWatchLogs event types are ignored"""
        template = Template(
            "",
            {
                "AWSTemplateFormatVersion": "2010-09-09",
                "Transform": "AWS::Serverless-2016-10-31",
                "Resources": {
                    "LogSubscriptionFunction": {
                        "Type": "AWS::Serverless::Function",
                        "Properties": {
                            "CodeUri": "hello_world/",
                            "Handler": "app.lambda_handler",
                            "Runtime": "python3.9",
                            "Events": {
                                "ApiEvent": {
                                    "Type": "Api",
                                    "Properties": {"Path": "/hello", "Method": "get"},
                                },
                                "ScheduleEvent": {
                                    "Type": "Schedule",
                                    "Properties": {"Schedule": "rate(1 minute)"},
                                },
                            },
                        },
                    },
                },
            },
        )
        matches = rule.match(template)
        assert len(matches) == 0


class TestEventsLogGroupNameGuardBranches:
    """Tests that exercise defensive guard branches for coverage"""

    def test_subscription_filter_non_dict_properties(self, rule):
        """Test SubscriptionFilter with non-dict Properties (line 60)"""
        template = Template(
            "",
            {
                "AWSTemplateFormatVersion": "2010-09-09",
                "Resources": {
                    "BadFilter": {
                        "Type": "AWS::Logs::SubscriptionFilter",
                        # Properties is a string instead of dict
                        "Properties": "not-a-dict",
                    },
                },
            },
        )
        # Should skip the resource and not crash
        matches = rule.match(template)
        assert len(matches) == 0

    def test_sam_function_non_dict_properties(self, rule):
        """Test SAM Function with non-dict Properties (line 76)"""
        template = Template(
            "",
            {
                "AWSTemplateFormatVersion": "2010-09-09",
                "Transform": "AWS::Serverless-2016-10-31",
                "Resources": {
                    "BadFunction": {
                        "Type": "AWS::Serverless::Function",
                        # Properties is a string instead of dict
                        "Properties": "not-a-dict",
                    },
                },
            },
        )
        # Should skip the resource and not crash
        matches = rule.match(template)
        assert len(matches) == 0

    def test_sam_function_non_dict_events(self, rule):
        """Test SAM Function with non-dict Events value (line 79)"""
        template = Template(
            "",
            {
                "AWSTemplateFormatVersion": "2010-09-09",
                "Transform": "AWS::Serverless-2016-10-31",
                "Resources": {
                    "FunctionWithBadEvents": {
                        "Type": "AWS::Serverless::Function",
                        "Properties": {
                            "CodeUri": "hello_world/",
                            "Handler": "app.lambda_handler",
                            "Runtime": "python3.9",
                            # Events is a string instead of dict
                            "Events": "not-a-dict",
                        },
                    },
                },
            },
        )
        # Should skip the Events and not crash
        matches = rule.match(template)
        assert len(matches) == 0

    def test_sam_function_non_dict_event_entry(self, rule):
        """Test SAM Function with non-dict individual event (line 83)"""
        template = Template(
            "",
            {
                "AWSTemplateFormatVersion": "2010-09-09",
                "Transform": "AWS::Serverless-2016-10-31",
                "Resources": {
                    "FunctionWithBadEvent": {
                        "Type": "AWS::Serverless::Function",
                        "Properties": {
                            "CodeUri": "hello_world/",
                            "Handler": "app.lambda_handler",
                            "Runtime": "python3.9",
                            "Events": {
                                # Event value is a string instead of dict
                                "BadEvent": "not-a-dict",
                            },
                        },
                    },
                },
            },
        )
        # Should skip the event and not crash
        matches = rule.match(template)
        assert len(matches) == 0

    def test_sam_cloudwatchlogs_non_dict_event_properties(self, rule):
        """Test CloudWatchLogs event with non-dict Properties (line 88)"""
        template = Template(
            "",
            {
                "AWSTemplateFormatVersion": "2010-09-09",
                "Transform": "AWS::Serverless-2016-10-31",
                "Resources": {
                    "FunctionWithBadEventProps": {
                        "Type": "AWS::Serverless::Function",
                        "Properties": {
                            "CodeUri": "hello_world/",
                            "Handler": "app.lambda_handler",
                            "Runtime": "python3.9",
                            "Events": {
                                "BadCloudWatchEvent": {
                                    "Type": "CloudWatchLogs",
                                    # Properties is a string instead of dict
                                    "Properties": "not-a-dict",
                                },
                            },
                        },
                    },
                },
            },
        )
        # Should skip the event and not crash
        matches = rule.match(template)
        assert len(matches) == 0

    def test_sam_cloudwatchlogs_missing_loggroupname(self, rule):
        """Test CloudWatchLogs event with missing LogGroupName (line 91)"""
        template = Template(
            "",
            {
                "AWSTemplateFormatVersion": "2010-09-09",
                "Transform": "AWS::Serverless-2016-10-31",
                "Resources": {
                    "FunctionWithMissingLogGroup": {
                        "Type": "AWS::Serverless::Function",
                        "Properties": {
                            "CodeUri": "hello_world/",
                            "Handler": "app.lambda_handler",
                            "Runtime": "python3.9",
                            "Events": {
                                "IncompleteEvent": {
                                    "Type": "CloudWatchLogs",
                                    "Properties": {
                                        # LogGroupName is missing
                                        "FilterPattern": "",
                                    },
                                },
                            },
                        },
                    },
                },
            },
        )
        # Should skip the event and not crash
        matches = rule.match(template)
        assert len(matches) == 0

    def test_sam_cloudwatchlogs_null_loggroupname(self, rule):
        """Test CloudWatchLogs event with explicit null LogGroupName (line 91)"""
        template = Template(
            "",
            {
                "AWSTemplateFormatVersion": "2010-09-09",
                "Transform": "AWS::Serverless-2016-10-31",
                "Resources": {
                    "FunctionWithNullLogGroup": {
                        "Type": "AWS::Serverless::Function",
                        "Properties": {
                            "CodeUri": "hello_world/",
                            "Handler": "app.lambda_handler",
                            "Runtime": "python3.9",
                            "Events": {
                                "NullLogGroupEvent": {
                                    "Type": "CloudWatchLogs",
                                    "Properties": {
                                        "LogGroupName": None,
                                        "FilterPattern": "",
                                    },
                                },
                            },
                        },
                    },
                },
            },
        )
        # Should skip the event and not crash
        matches = rule.match(template)
        assert len(matches) == 0
