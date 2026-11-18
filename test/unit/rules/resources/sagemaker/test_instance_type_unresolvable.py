"""
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
"""

import pytest

from cfnlint import api

_INSTANCE_TYPE_RULES = ("E3640", "E3642", "E3643", "E3644")

_TEMPLATE = """
Parameters:
  InstanceType:
    Type: String
Conditions:
  IsProd: !Equals [!Ref InstanceType, prod]
Resources:
  Bucket:
    Type: AWS::S3::Bucket
  Cluster:
    Type: AWS::SageMaker::Cluster
    Properties:
      ClusterName: cluster
      InstanceGroups:
        - InstanceGroupName: fromRef
          InstanceType: !Ref InstanceType
          InstanceCount: 1
          ExecutionRole: arn:aws:iam::123456789012:role/role
          LifeCycleConfig:
            SourceS3Uri: s3://amzn-s3-demo-bucket/lifecycle/
            OnCreate: on_create.sh
        - InstanceGroupName: fromIf
          InstanceType: !If [IsProd, ml.p5e.48xlarge, ml.m5.large]
          InstanceCount: 1
          ExecutionRole: arn:aws:iam::123456789012:role/role
          LifeCycleConfig:
            SourceS3Uri: s3://amzn-s3-demo-bucket/lifecycle/
            OnCreate: on_create.sh
        - InstanceGroupName: fromGetAtt
          InstanceType: !GetAtt Bucket.Arn
          InstanceCount: 1
          ExecutionRole: arn:aws:iam::123456789012:role/role
          LifeCycleConfig:
            SourceS3Uri: s3://amzn-s3-demo-bucket/lifecycle/
            OnCreate: on_create.sh
  Experiment:
    Type: AWS::SageMaker::InferenceExperiment
    Properties:
      Name: experiment
      Type: ShadowMode
      RoleArn: arn:aws:iam::123456789012:role/role
      EndpointName: endpoint
      ModelVariants:
        - ModelName: model
          VariantName: VariantA
          InfrastructureConfig:
            InfrastructureType: RealTimeInference
            RealTimeInferenceConfig:
              InstanceType: !Ref InstanceType
              InstanceCount: 1
      ShadowModeConfig:
        SourceModelVariantName: VariantA
        ShadowModelVariants:
          - ShadowModelVariantName: VariantA
            SamplingPercentage: 50
  Package:
    Type: AWS::SageMaker::ModelPackage
    Properties:
      ModelPackageGroupName: group
      InferenceSpecification:
        Containers:
          - Image: 123456789012.dkr.ecr.us-east-1.amazonaws.com/image:latest
        SupportedContentTypes: [text/csv]
        SupportedResponseMIMETypes: [text/csv]
      ValidationSpecification:
        ValidationRole: arn:aws:iam::123456789012:role/role
        ValidationProfiles:
          - ProfileName: profile
            TransformJobDefinition:
              TransformInput:
                DataSource:
                  S3DataSource:
                    S3DataType: S3Prefix
                    S3Uri: s3://amzn-s3-demo-bucket/in
              TransformOutput:
                S3OutputPath: s3://amzn-s3-demo-bucket/out
              TransformResources:
                InstanceCount: 1
                InstanceType: !If [IsProd, ml.p3.2xlarge, ml.m5.large]
  Monitoring:
    Type: AWS::SageMaker::MonitoringSchedule
    Properties:
      MonitoringScheduleName: schedule
      MonitoringScheduleConfig:
        MonitoringJobDefinition:
          RoleArn: arn:aws:iam::123456789012:role/role
          MonitoringAppSpecification:
            ImageUri: 123456789012.dkr.ecr.us-east-1.amazonaws.com/monitor:latest
          MonitoringInputs:
            - EndpointInput:
                EndpointName: endpoint
                LocalPath: /opt/ml/processing/input
          MonitoringOutputConfig:
            MonitoringOutputs:
              - S3Output:
                  LocalPath: /opt/ml/processing/output
                  S3Uri: s3://amzn-s3-demo-bucket/out
          MonitoringResources:
            ClusterConfig:
              InstanceCount: 1
              InstanceType: !Ref InstanceType
              VolumeSizeInGB: 20
"""


@pytest.mark.parametrize("region", ["us-east-1", "ap-southeast-5"])
def test_unresolvable_instance_types_are_silent(region):
    """An instance type behind a function must not be reported."""
    matches = api.lint(_TEMPLATE, regions=[region])

    assert not [m for m in matches if m.rule.id in _INSTANCE_TYPE_RULES], (
        f"Got instance type errors in {region}: {matches!r}"
    )
