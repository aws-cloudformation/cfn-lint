# Services Missing from AWS Smithy API Models

## Overview

These AWS services have CloudFormation resources with boto patches but do not exist in the AWS Smithy API models repository. They are likely legacy or deprecated services.

## Missing Services

### 1. OpsWorks (opsworks)
**Status**: Legacy service
**Resources affected**:
- `AWS::OpsWorks::Instance`
- `AWS::OpsWorks::Layer`

**Note**: AWS OpsWorks Stacks is in maintenance mode. AWS recommends migrating to AWS Systems Manager or other modern solutions.

### 2. OpsWorks CM (opsworkscm)
**Status**: Legacy service
**Resources affected**:
- `AWS::OpsWorksCM::Server`

**Note**: AWS OpsWorks for Chef Automate and Puppet Enterprise is in maintenance mode.

### 3. RoboMaker (robomaker)
**Status**: Service discontinued
**Resources affected**:
- `AWS::RoboMaker::Robot`
- `AWS::RoboMaker::RobotApplication`
- `AWS::RoboMaker::RobotApplicationVersion`
- `AWS::RoboMaker::SimulationApplication`
- `AWS::RoboMaker::SimulationApplicationVersion`

**Note**: AWS RoboMaker was discontinued on September 10, 2024. The service is no longer available for new customers.

### 4. Lookout for Metrics (lookoutmetrics)
**Status**: Service discontinued
**Resources affected**:
- `AWS::LookoutMetrics::AnomalyDetector`

**Note**: Amazon Lookout for Metrics was discontinued. Only Lookout for Equipment remains in Smithy models.

## Impact

These 4 services account for **9 resources** that will only have boto patches and no Smithy patches. This is expected and acceptable since:

1. The services are no longer actively developed
2. Boto patches provide sufficient validation for existing templates
3. New templates should not use these services

## Recommendation

- **Keep boto patches** for these resources to support existing templates
- **Document** that these services are legacy/deprecated
- **Consider adding warnings** in cfn-lint when these resources are detected

## Total Coverage After Migration

With all service name mappings added:
- **Expected boto-only resources**: ~9 (legacy services)
- **Expected both boto and smithy**: ~600+ resources
- **Smithy provides better coverage** for all active services
