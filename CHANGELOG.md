### 0.25.1
###### CloudFormation Specifications
- Update allowed values for AWS Config types (pull #[1197](https://github.com/aws-cloudformation/cfn-python-lint/pull/1197))
- Update CloudFormation specs to 8.1.0 (pull #[1197](https://github.com/aws-cloudformation/cfn-python-lint/pull/1197))

### 0.25.0
###### Features
- Add rule [I1022](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#I1022) to recommend Sub over Join when join is using empty delimiter (pull #[1067](https://github.com/aws-cloudformation/cfn-python-lint/pull/1067))
- Remove setuptools requirement (pull #[1188](https://github.com/aws-cloudformation/cfn-python-lint/pull/1188))
###### CloudFormation Specifications
- Update Lambda runtime versions EOL date (pull #[1180](https://github.com/aws-cloudformation/cfn-python-lint/pull/1180))
- Update CloudFormation specs to 8.0.0 (pull #[1187](https://github.com/aws-cloudformation/cfn-python-lint/pull/1187))
- Update Pricing and SSM data to 2019.11.08 (pull #[1187](https://github.com/aws-cloudformation/cfn-python-lint/pull/1187))
###### Fixes
- Update rule [W2501](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#W2501) to include more properties to validate security of a parameter (pull #[1181](https://github.com/aws-cloudformation/cfn-python-lint/pull/1181))
- Fix YAML parsing to not fail on merging and aliases (pull #[1182](https://github.com/aws-cloudformation/cfn-python-lint/pull/1182))
- Fix an issue with SAM when CORS is present in pre-transformed template (pull #[1185](https://github.com/aws-cloudformation/cfn-python-lint/pull/1185))
- Update rule [W7001](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#W7001) to look at pre-transformed FindInMaps (pull #[1186](https://github.com/aws-cloudformation/cfn-python-lint/pull/1186))


### 0.24.8
###### CloudFormation Specifications
- Update CloudFormation specs to 7.2.0 (pull #[1177](https://github.com/aws-cloudformation/cfn-python-lint/pull/1177))
- Update Pricing and SSM data to 2019.11.01 (pull #[1177](https://github.com/aws-cloudformation/cfn-python-lint/pull/1177))


### 0.24.7
###### CloudFormation Specifications
- Patch in Tags for SNS Topics (pull #[1174](https://github.com/aws-cloudformation/cfn-python-lint/pull/1174))
- Update Pricing and SSM data to 2019.10.31 (pull #[1175](https://github.com/aws-cloudformation/cfn-python-lint/pull/1175))
###### Fixes
- Consolidate PSEUDOPARAMS into cfnlint.helpers (pull #[1172](https://github.com/aws-cloudformation/cfn-python-lint/pull/1172))


### 0.24.6
###### Features
- Update SAM Translator to 1.15.1 (pull #[1166](https://github.com/aws-cloudformation/cfn-python-lint/pull/1166))

### 0.24.5
###### CloudFormation Specifications
- Update CloudFormation specs to 7.1.0 (pull #[1163](https://github.com/aws-cloudformation/cfn-python-lint/pull/1163))
- Update Pricing and SSM data to 2019.10.21 (pull #[1163](https://github.com/aws-cloudformation/cfn-python-lint/pull/1163))
###### Fixes
- Update rule [E2532](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E2532) to support parameters inside a map type (pull #[1164](https://github.com/aws-cloudformation/cfn-python-lint/pull/1164))
- Update rule [E2510](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E2510) to allow SSM parameter types for CIDR blocks (pull #[1162](https://github.com/aws-cloudformation/cfn-python-lint/pull/1162))


### 0.24.4
###### CloudFormation Specifications
- Update CloudFormation specs to 6.3.0 (pull #[1155](https://github.com/aws-cloudformation/cfn-python-lint/pull/1155))
- Update Pricing and SSM data to 2019.10.05 (pull #[1155](https://github.com/aws-cloudformation/cfn-python-lint/pull/1155))
- Update Update CloudWatch alarm comparison operators (pull #[1154](https://github.com/aws-cloudformation/cfn-python-lint/pull/1154))
###### Fixes
- Update rule [E1022](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E1022) to allow lists in custom resources (pull #[1151](https://github.com/aws-cloudformation/cfn-python-lint/pull/1151))


### 0.24.3
###### Features
- Add link to updated IntelliJ integration (pull #[1138](https://github.com/aws-cloudformation/cfn-python-lint/pull/1138))
- Add link to emacs integration (pull #[1118](https://github.com/aws-cloudformation/cfn-python-lint/pull/1118))
###### CloudFormation Specifications
- Update CloudFormation specs to 6.2.0 (pull #[1145](https://github.com/aws-cloudformation/cfn-python-lint/pull/1145))
- Update Pricing and SSM data to 2019.09.28 (pull #[1145](https://github.com/aws-cloudformation/cfn-python-lint/pull/1145))
- Remove manual patches that are no longer needed (pull #[1146](https://github.com/aws-cloudformation/cfn-python-lint/pull/1146))
- Update CloudFormation spec links for a few regions that using old links (pull #[1148](https://github.com/aws-cloudformation/cfn-python-lint/pull/1148))
###### Fixes
- Update rule [E3001](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3001) to allow `DeletionPolicy` and `UpdateReplacePolciy` to be allowed on all resources (pull #[1139](https://github.com/aws-cloudformation/cfn-python-lint/pull/1139))
- Update rule [W2030](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#W2030) to not check Paramter default values when using a Resource Condition (pull #[1140](https://github.com/aws-cloudformation/cfn-python-lint/pull/1140))
- Update rule [E2532](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E2532) to allow new types in Step Functions (pull #[1143](https://github.com/aws-cloudformation/cfn-python-lint/pull/1143))


### 0.24.2
###### CloudFormation Specifications
- Add missing values for LifecyclePolicy API (pull #[1128](https://github.com/aws-cloudformation/cfn-python-lint/pull/1128))
- Update CloudFormation specs to 6.1.0 (pull #[1134](https://github.com/aws-cloudformation/cfn-python-lint/pull/1134))
- Update Pricing and SSM data to 2019.09.20 (pull #[1134](https://github.com/aws-cloudformation/cfn-python-lint/pull/1134))
###### Fixes
- Update [E1029](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E1029)
to include cognito-identity keys to list of excluded resourse when checking if Fn sub is needed (pull #[1136](https://github.com/aws-cloudformation/cfn-python-lint/pull/1136))


### 0.24.1
###### CloudFormation Specifications
- Update CloudFormation specs to 6.0.0 (pull #[1126](https://github.com/aws-cloudformation/cfn-python-lint/pull/1126))
###### Fixes
- Update AWS::SQS::Queue.ReceiveMessageWaitTimeSeconds to allow 0 value (pull #[1123](https://github.com/aws-cloudformation/cfn-python-lint/pull/1123))
- AWS::EC2::SecurityGroup.Description StringMin and StringMax should be integers (pull #[1125](https://github.com/aws-cloudformation/cfn-python-lint/pull/1125))
- AWS::ApiGateway::GatewayResponse.ResponseType typo (pull #[1126](https://github.com/aws-cloudformation/cfn-python-lint/pull/1126))

### 0.24.0
###### Features
- Move rule classes from cfnlint into cfnlint.rules (pull #[1098](https://github.com/aws-cloudformation/cfn-python-lint/pull/1098))
###### CloudFormation Specifications
- Update IAM policies as of 2019.09.03 (pull #[1120](https://github.com/aws-cloudformation/cfn-python-lint/pull/1120))
- Update CloudFormation specs from pricing and SSM data as of 2019.09.03 (pull #[1120](https://github.com/aws-cloudformation/cfn-python-lint/pull/1120))
- Add a lot of min/max values to the specs (pull #[1110](https://github.com/aws-cloudformation/cfn-python-lint/pull/1110) and pull #[1116](https://github.com/aws-cloudformation/cfn-python-lint/pull/1116))
###### Fixes
- Add me-south-1 to supported regions (pull #[1113](https://github.com/aws-cloudformation/cfn-python-lint/pull/1113))
- Fix an issue where the spec file was referencing instance profiles for Glue Resources (pull #[1114](https://github.com/aws-cloudformation/cfn-python-lint/pull/1114))

### 0.23.5
###### CloudFormation Specifications
- Switch AWS Batch SpotIamFleetRole to Role Arn (pull #[1111](https://github.com/aws-cloudformation/cfn-python-lint/pull/1111))

### 0.23.4
###### CloudFormation Specifications
- Update CloudFormatin specs to 5.3.0 (pull #[1108](https://github.com/aws-cloudformation/cfn-python-lint/pull/1108))
- Update CloudFormatin specs from pricing and SSM data on 2019.08.22 (pull #[1104](https://github.com/aws-cloudformation/cfn-python-lint/pull/1104))
- Add 416 to the CloudFront Error Codes (pull #[1100](https://github.com/aws-cloudformation/cfn-python-lint/pull/1100))
- Move a lot of types into separate files (pull #[1074](https://github.com/aws-cloudformation/cfn-python-lint/pull/1074))
###### Fixes
- Don't fail getting directives when resources are malformed (pull #[1099](https://github.com/aws-cloudformation/cfn-python-lint/pull/1099))

### 0.23.3
###### CloudFormation Specifications
- Add me-east-1 CloudFormation spec (pull #[1095](https://github.com/aws-cloudformation/cfn-python-lint/pull/1095))
- Update CloudFormatin specs to 5.1.0 (pull #[1093](https://github.com/aws-cloudformation/cfn-python-lint/pull/1093))
- Update spec patching from SSM and pricing to 2019.08.13 (pull #[1093](https://github.com/aws-cloudformation/cfn-python-lint/pull/1093))
###### Fixes
- Remove requests and switch to urllib(2) (pull #[1093](https://github.com/aws-cloudformation/cfn-python-lint/pull/1093))
- Fix rule [E3003](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3003) to not fail when running into a basic property in the CloudFormation spec (pull #[1096](https://github.com/aws-cloudformation/cfn-python-lint/pull/1096))

### 0.23.2
###### CloudFormation Specifications
- Update CloudFormation spec to version 5.0.0 (pull #[1087](https://github.com/aws-cloudformation/cfn-python-lint/pull/1087))
- Remove Ref check from IAM Policy Name (pull #[1087](https://github.com/aws-cloudformation/cfn-python-lint/pull/1087))

### 0.23.1
###### Fixes
- Fix an issue where anything piped into cfn-lint would result in ignoring the templates parameter (pull #[1081](https://github.com/aws-cloudformation/cfn-python-lint/pull/1081))

### 0.23.0
###### Features
- Add support for regions cn-north-1 and cn-northwest-1 (pull #[1051](https://github.com/aws-cloudformation/cfn-python-lint/pull/1051))
- Add rule [E3027](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3027) to validate the format of AWS Event ScheduleExpression (pull #[1028](https://github.com/aws-cloudformation/cfn-python-lint/pull/1028))
- Update SAM Translator support to release 1.13.0 (pull #[1054](https://github.com/aws-cloudformation/cfn-python-lint/pull/1054))
- Extend rule [W2509](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#W2509) and [E2004](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E2004) to check for more types of CIDR properties (pull #[1058](https://github.com/aws-cloudformation/cfn-python-lint/pull/1058))
- Add Availability Zones for me-south-1 region (pull #[1070](https://github.com/aws-cloudformation/cfn-python-lint/pull/1070))
- Update README to document using cfn-lint with github actions (pull #[1072](https://github.com/aws-cloudformation/cfn-python-lint/pull/1072))
###### CloudFormation Specifications
- Restructure some of the patching to make organization easier (pull #[1030](https://github.com/aws-cloudformation/cfn-python-lint/pull/1030))
- Update specs from pricing and SSM data as of 2019.08.01 (pull #[1078](https://github.com/aws-cloudformation/cfn-python-lint/pull/1078))
- Remove IAM::User Tags and move IAM::Role Tag support to regions where it works (pull #[1077](https://github.com/aws-cloudformation/cfn-python-lint/pull/1077))
###### Fixes
- Apply SAM Transform when template Transforms are a list (pull #[1056](https://github.com/aws-cloudformation/cfn-python-lint/pull/1056))
- Fix an issue where templates provided via stdin where not getting linted (pull #[1060](https://github.com/aws-cloudformation/cfn-python-lint/pull/1060))
- Fix rule [E2015](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E2015) to convert integers to string when testing min/max length (pull #[1063](https://github.com/aws-cloudformation/cfn-python-lint/pull/1063))
- Update excludes for [E1029](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E1029) to include TopicRulePayload (pull #[1066](https://github.com/aws-cloudformation/cfn-python-lint/pull/1066))

### 0.22.4
###### Features
- Add ALL_REGIONS option for -r flag (pull #[1026](https://github.com/aws-cloudformation/cfn-python-lint/pull/1026))
###### CloudFormation Specifications
- Add SSM parameter type values to [E2510](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E2510) (pull #[1036](https://github.com/aws-cloudformation/cfn-python-lint/pull/1036))
- Add allowed values for AWS::IAM Resources (pull #[1027](https://github.com/aws-cloudformation/cfn-python-lint/pull/1027))
- Update CloudFormation spec to version 4.3.0 (pull #[1048](https://github.com/aws-cloudformation/cfn-python-lint/pull/1048))
- Update specs from pricing and SSM data as of 2019.07.25
###### Fixes
- Removed duplicate from list of Availability Zones (pull #[1035](https://github.com/aws-cloudformation/cfn-python-lint/pull/1035))
- Fixed example regex in CIDR rule (pull #[1029](https://github.com/aws-cloudformation/cfn-python-lint/pull/1029))
- Support for Serverless transform when it's in a list of one Transforms (pull #[1042](https://github.com/aws-cloudformation/cfn-python-lint/pull/1042))
- Don't fail rules that include a Transform (pull #[1041](https://github.com/aws-cloudformation/cfn-python-lint/pull/1041))
- Don't fail when AWS::NoValue used when we're looking for a list (pull #[1039](https://github.com/aws-cloudformation/cfn-python-lint/pull/1039))
- Fixed [E3002](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3002) to support AWS::NoValue (pull #[1038](https://github.com/aws-cloudformation/cfn-python-lint/pull/1038))
- Added FindInMap as valid function within Fn::Cidr (pull #[1034](https://github.com/aws-cloudformation/cfn-python-lint/pull/1034))

### 0.22.3
###### CloudFormation Specifications
- Patch in `AWS::SageMaker::CodeRepository` to the CloudFormation spec (issue #[1005](https://github.com/aws-cloudformation/cfn-python-lint/issues/1005))
- Patch in Tags into IAM Roles and Users (issue #[1015](https://github.com/aws-cloudformation/cfn-python-lint/issues/1015))
- Update CloudFormation spec to version 4.2.0 (pull #[1023](https://github.com/aws-cloudformation/cfn-python-lint/pull/1023))
- Update specs from pricing and SSM data as of 2019.07.13
###### Fixes
- Add more Availability Zones (pull #[1021](https://github.com/aws-cloudformation/cfn-python-lint/pull/1021))

### 0.22.2
###### CloudFormation Specifications
- Patch in `AWS::Cognito::UserPool` resource information for `ap-south-1` and `ap-southeast-1` (issue #[1002](https://github.com/aws-cloudformation/cfn-python-lint/issues/1002))
- Remove manual patching for `AWS::Backup::BackupPlan` resource information and fix a few spec issues (pull #[1006](https://github.com/aws-cloudformation/cfn-python-lint/pull/1006))
- Fix a few spec regex patterns that were missing escapes of `-` inside `[]` (issue #[997](https://github.com/aws-cloudformation/cfn-python-lint/issues/997))
- Update pricing script to include bare metal instance types (issue #[998](https://github.com/aws-cloudformation/cfn-python-lint/issue/998))
- Create a regex pattern for IAM Policy Names (issue #[996](https://github.com/aws-cloudformation/cfn-python-lint/issues/996))
- Patch CloudFormation specs from SSM data on 2019.07.10
###### Fixes
- Fix a warning when loading resources using a `\` in the prefix (issue #[1009](https://github.com/aws-cloudformation/cfn-python-lint/issues/1009))


### 0.22.1
###### CloudFormation Specifications
- Add `INSTANCE` to `DLMPolicyResourceType` allowed values (pull #[995](https://github.com/aws-cloudformation/cfn-python-lint/pull/995))
- Update specs from weird 4.1.0 release (pull #[994](https://github.com/aws-cloudformation/cfn-python-lint/pull/994))
- Update instance types and patches from SSM to date 2019.07.04 (pull #[1001](https://github.com/aws-cloudformation/cfn-python-lint/pull/1001))
- Add all the allowed values of the AWS::EFS Resources (pull #[990](https://github.com/aws-cloudformation/cfn-python-lint/pull/990))
###### Fixes
- Fix an issue where rules were being loaded twice (pull #[980](https://github.com/aws-cloudformation/cfn-python-lint/pull/980))
- Fix an issue with rule [E1010](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E1010) to split GetAtt strings into two values (issue #[986](https://github.com/aws-cloudformation/cfn-python-lint/issues/986))
- Update rules [E8004](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E8004), [E8003](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E8003), [E8005](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E8005), and [E8006](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E8006) to not flag functions used in Service Catalog rules section (issue #[979](https://github.com/aws-cloudformation/cfn-python-lint/issues/979))
- Patched testing for Lambda Runtime EOL and end dates to test as if a specific date (pull #[999](https://github.com/aws-cloudformation/cfn-python-lint/pull/999))

### 0.22.0
###### CloudFormation Specifications
- Update specs to 4.1.0
- Added LaunchTemplateId/LaunchTemplateName of the AutoScalingGroup to the OnlyOne
- Patch resource AWS::EC2::LaunchTemplate property TagSpecifications
- Add AWS::EC2::LaunchTemplate property to LaunchTemplateName min/max/pattern
- Add AWS::EC2::LaunchTemplate allowed values for the ResourceType property
- Remove/Add services to region tables based on SSM endpoints
###### Fixes
- Update JsonSchem to 3.0 to support the new version 1.12.0 of aws-sam-translator
- Update rule [E2503](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E2503) to allow NLBs to use UDP
- Update rule [E3020](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3020) to include many special characters for DNS records
- Sort filenames when getting a bunch of templates from a folder
- Fix typos in the integration documentation

### 0.21.6
###### Features
- Remove rule [W2507](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#W2507) and use rule [E3008](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3008) instead
- Remove rule [W2508](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#W2508) and use rule [E3008](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3008) instead
###### CloudFormation Specifications
- Update specs to 3.4.0
- Add all the allowed values of the AWS::ECS Resources.
- Update CloudFormation Spec to include the Backup Resources
- Add Cognito RefreshTokenValidity number limits
###### Fixes
- Fix copy-paste typo in Not function check
- Don't fail when conditions are used with parameters and allowed values
- More IAM Resource exceptions for Sub Needed check

### 0.21.5
###### Features
- Update rule [E3001](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3001) to validate that a Resource Condition is a string
###### CloudFormation Specifications
- Add all the allowed values of the AWS::EC2 CapacityReservation Resources
- Update Launch Configuration IamInstanceProfile to support Ref or GetAtt to an IAM Instance Profile
###### Fixes
- Fix `lessthan` type in a bunch of rules
- Update rule [E2507](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E2507) to handle intrinsics when testing the values for `Effect`
- Fix rule [E8002](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E8002) to not error when the Condition isn't a string

### 0.21.4
###### Features
- Include more resource types in [W3037](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#W30307)
###### CloudFormation Specifications
- Add Resource Type `AWS::CDK::Metadata`
###### Fixes
- Uncap requests dependency in setup.py
- Check Join functions have lists in the correct sections
- Pass a parameter value for AutoPublishAlias when doing a Transform
- Show usage examples when displaying the help

### 0.21.3
###### Fixes
- Support dumping strings for datetime objects when doing a Transform

### 0.21.2
###### CloudFormation Specifications
- Update CloudFormation specs to 3.3.0
- Update instance types from pricing API as of 2019.05.23

### 0.21.1
###### Features
- Add `Info` logging capability and set the default logging to `NotSet`
###### Fixes
- Only do rule logging (start/stop/time) when the rule is going to be called
- Update rule [E1019](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E1019) to allow `Fn::Transform` inside a `Fn::Sub`
- Update rule [W2001](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#W2001) to not break when `Fn::Transform` inside a `Fn::Sub`
- Update rule [E2503](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E2503) to allow conditions to be used and to not default to `network` load balancer when an object is used for the Load Balancer type

### 0.21.0
###### Features
- New rule [E3038](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3038) to check if a Serverless resource includes the appropriate Transform
- New rule [E2531](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E2531) to validate a Lambda's runtime against the deprecated dates
- New rule [W2531](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#W2531) to validate a Lambda's runtime against the EOL dates
- Update rule [E2541](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E2541) to include updates to Code Pipeline capabilities
- Update rule [E2503](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E2503) to include checking of values for load balancer attributes
###### CloudFormation Specifications
- Update CloudFormation specs to 3.2.0
- Update instance types from pricing API as of 2019.05.20
###### Fixes
- Include setuptools in setup.py requires

### 0.20.3
###### CloudFormation Specifications
- Update instance types from pricing API as of 2019.05.16
###### Fixes
- Update [E7001](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E7001) to allow float/doubles for mapping values
- Update [W1020](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#W1020) to check pre-transformed Fn::Sub(s) to determine if a Sub is needed
- Pin requests to be below or equal to 2.21.0 to prevent issues with botocore

### 0.20.2
###### Features
- Add support for List<String> Parameter types
###### CloudFormation Specifications
- Add allowed values for AWS::EC2 EIP, FlowLog, CustomerGateway, DHCPOptions, EC2Fleet
- Create new property type for Security Group IDs or Names
- Add new Lambda runtime environment for NodeJs 10.x
- Move AWS::ServiceDiscovery::Service Health checks from Only One to Exclusive
- Update Glue Crawler Role to take an ARN or a name
- Remove PrimitiveType from MaintenanceWindowTarget Targets
- Add Min/Max values for Load Balancer Ports to be between 1-65535
###### Fixes
- Include License file in the pypi package to help with downstream projects
- Filter out dynamic references from rule [E3031](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3031) and [E3030](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3030)
- Convert Python linting and Code Coverage from Python 3.6 to 3.7

### 0.20.1
###### Fixes
- Update rule [E8003](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E8003) to support more functions inside a Fn::Equals

### 0.20.0
###### Features
- Allow a rule's exception to be defined in a [resource's metadata](https://github.com/kddejong/cfn-python-lint/tree/Release/v0.20.0#resource-based-metadata)
- Add rule [configuration capabilities](https://github.com/kddejong/cfn-python-lint/tree/Release/v0.20.0#configure-rules)
- Update rule [E3012](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3012) to allow for non strict property checking
- Add rule [E8003](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E8003) to test Fn::Equals structure and syntax
- Add rule [E8004](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E8004) to test Fn::And structure and syntax
- Add rule [E8005](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E8005) to test Fn::Not structure and syntax
- Add rule [E8006](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E8006) to test Fn::Or structure and syntax
- Include Path to error in the JSON output
- Update documentation to describe how to install cfn-lint from brew
###### CloudFormation Specifications
- Update CloudFormation specs to version 3.0.0
- Add new region ap-east-1
- Add list min/max and string min/max for CloudWatch Alarm Actions
- Add allowed values for EC2::LaunchTemplate
- Add allowed values for EC2::Host
- Update allowed values for Amazon MQ to include 5.15.9
- Add AWS::Greengrass::ResourceDefinition to GreenGrass supported regions
- Add AWS::EC2::VPCEndpointService to all regions
- Update AWS::ECS::TaskDefinition ExecutionRoleArn to be a IAM Role ARN
- Patch spec files for SSM MaintenanceWindow to look for Target and not Targets
- Update ManagedPolicyArns list size to be 20 which is the hard limit.  10 is the soft limit.
###### Fixes
- Fix rule [E3033](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3033) to check the string size when the string is inside a list
- Fix an issue in which AWS::NotificationARNs was not a list
- Add AWS::EC2::Volume to rule [W3010](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#W3010)
- Fix an issue with [W2001](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#W2001) where SAM translate would remove the Ref to a parameter causing this error to falsely trigger
- Fix rule [W3010](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#W3010) to not error when the availability zone is 'all'

### 0.19.1
###### Fixes
- Fix core Condition processing to support direct Condition in another Condition
- Fix the W2030 to check numbers against string allowed values

### 0.19.0
###### Features
- Add NS and PTR Route53 record checking to rule [E3020](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3020)
- New rule [E3050](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3050) to check if a Ref to IAM Role has a Role path of '/'
- New rule [E3037](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3037) to look for duplicates in a list that doesn't support duplicates
- New rule [I3037](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#I3037) to look for duplicates in a list when duplicates are allowed
###### CloudFormation Specifications
- Add Min/Max values to AWS::ElasticLoadBalancingV2::TargetGroup HealthCheckTimeoutSeconds
- Add Max JSON size to AWS::IAM::ManagedPolicy PolicyDocument
- Add allowed values for AWS::EC2 SpotFleet, TransitGateway, NetworkAcl
NetworkInterface, PlacementGroup, and Volume
- Add Min/max values to AWS::Budgets::Budget.Notification Threshold
- Update RDS Instance types by database engine and license definitions using the pricing API
- Update AWS::CodeBuild::Project ServiceRole to support Role Name or ARN
- Update AWS::ECS::Service Role to support Role Name or ARN
###### Fixes
- Update [E3025](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3025) to support the new structure of data in the RDS instance type json
- Update [E2540](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E2540) to remove all nested conditions from the object
- Update [E3030](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E2540) to not do strict type checking
- Update [E3020](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3020) to support conditions nested in the record sets
- Update [E3008](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3008) to better handle CloudFormation sub stacks with different GetAtt formats

### 0.18.1
###### CloudFormation Specifications
- Update CloudFormation Specs to 2.30.0
- Fix IAM Regex Path to support more character types
- Update AWS::Batch::ComputeEnvironment.ComputeResources InstanceRole to reference an
InstanceProfile or GetAtt the InstanceProfile Arn
- Allow VPC IDs to Ref a Parameter of type String
###### Fixes
- Fix [E3502](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3502) to check the size of the property instead of the parent object

### 0.18.0
###### Features
- New rule [E3032](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3032) to check the size of lists
- New rule [E3502](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3502) to check JSON Object Size using definitions in the spec file
- New rule [E3033](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3033) to test the minimum and maximum length of a string
- New rule [E3034](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3034) to validate the min and max of a number
- Remove Ebs Iops check from [E2504](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E2504) and use rule [E3034](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3034) instead
- Remove rule [E2509](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E2509) and use rule [E3033](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3033) instead
- Remove rule [E2508](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E2508) as it replaced by [E3032](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3032) and [E3502](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3502)
- Update rule [E2503](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E2503) to check that there are at least two 2 Subnets or SubnetMappings for ALBs
- SAM requirement upped to minimal version of 1.10.0
###### CloudFormation Specifications
- Extend specs to include:
  - `ListMin` and `ListMax` for the minimum and maximum size of a list
  - `JsonMax` to check the max size of a JSON Object
  - `StringMin` and `StringMax` to check the minimum and maximum length of a String
  - `NumberMin` and `NumberMax` to check the minimum and maximum value of a Number, Float, Long
- Update State and ExecutionRoleArn to be required on AWS::DLM::LifecyclePolicy
- Add AllowedValues for PerformanceInsightsRetentionPeriod for AWS::RDS::Instance
- Add AllowedValues for the AWS::GuardDuty Resources
- Add AllowedValues for AWS::EC2 VPC and VPN Resources
- Switch IAM Instance Profiles for certain resources to the type that only takes the name
- Add regex pattern for IAM Instance Profile when a name (not Arn) is used
- Add regex pattern for IAM Paths
- Add Regex pattern for IAM Role Arn
- Update OnlyOne spec to require require at least one of Subnets or SubnetMappings with ELB v2
###### Fixes
- Fix serverless transform to use DefinitionBody when Auth is in the API definition
- Fix rule [W2030](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#W2030) to not error when checking SSM or List Parameters

### 0.17.1
###### Features
- Update rule [E2503](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E2503) to make sure NLBs don't have a Security Group configured
###### CloudFormation Specifications
- Add all the allowed values of the `AWS::Glue` Resources
- Update OnlyOne check for `AWS::CloudWatch::Alarm` to only `MetricName` or `Metrics`
- Update Exclusive check for `AWS::CloudWatch::Alarm` for properties mixed with `Metrics` and `Statistic`
- Update CloudFormation specs to 2.29.0
- Fix type with MariaDB in the AllowedValues
- Update pricing information for data available on 2018.3.29
###### Fixes
- Fix rule [E1029](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E1029) to not look for a sub is needed when looking for iot strings in policies
- Fix rule [E2541](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E2541) to allow for ActionId Versions of length 1-9 and meets regex `[0-9A-Za-z_-]+`
- Fix rule [E2532](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E2532) to allow for `Parameters` inside a `Pass` action
- Fix an issue when getting the location of an error in which numbers are causing an attribute error

### 0.17.0
###### Features
- Add new rule [E3026](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3026) to validate Redis cluster settings including AutomaticFailoverEnabled and NumCacheClusters.  Status: Released
- Add new rule [W3037](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#W3037) to validate IAM resource policies.  Status: Experimental
- Add new parameter `-e/--include-experimental` to allow for new rules in that aren't ready to be fully released
###### CloudFormation Specifications
- Update Spec files to 2.28.0
- Add all the allowed values of the AWS::Redshift::* Resources
- Add all the allowed values of the AWS::Neptune::* Resources
- Patch spec to make AWS::CloudFront::Distribution.LambdaFunctionAssociation.LambdaFunctionARN required
- Patch spec to make AWS::DynamoDB::Table AttributeDefinitions required
###### Fixes
- Remove extra blank lines when there is no errors in the output
- Add exception to rule [E1029](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E1029) to have exceptions for EMR CloudWatchAlarmDefinition
- Update rule [E1029](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E1029) to allow for literals in a Sub
- Remove sub checks from rule [E3031](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3031) as it won't match in all cases of an allowed pattern regex check
- Correct typos for errors in rule [W1001](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#W1001)
- Switch from parsing a template as Yaml to Json when finding an escape character
- Fix an issue with SAM related to transforming templates with Serverless Application and Lambda Layers
- Fix an issue with rule [E2541](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E2541) when non strings were used for Stage Names

### 0.16.0
###### Features
- Add rule [E3031](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3031) to look for regex patterns based on the patched spec file
- Remove regex checks from rule [E2509](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E2509)
- Add parameter `ignore-templates` to allow the ignoring of templates when doing bulk linting
###### CloudFormation Specifications
- Update Spec files to 2.26.0
- Add all the allowed values of the AWS::DirectoryService::* Resources
- Add all the allowed values of the AWS::DynamoDB::* Resources
- Added AWS::Route53Resolver resources to the Spec Patches of ap-southeast-2
- Patch the spec file with regex patterns
- Add all the allowed values of the AWS::DocDb::* Resources
###### Fixes
- Update rule [E2504](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E2504) to have '20000' as the max value
- Update rule [E1016](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E1016) to not allow ImportValue inside of Conditions
- Update rule [E2508](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E2508) to check conditions when providing limit checks on managed policies
- Convert unicode to strings when in Py 3.4/3.5 and updating specs
- Convert from `awslabs` to `aws-cloudformation` organization
- Remove suppression of logging that was removed from samtranslator >1.7.0 and incompatibility with
samtranslator 1.10.0


### 0.15.0
###### Features
- Add scaffolding for arbitrary Match attributes, adding attributes for Type checks
- Add rule [E3024](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3024) to validate that ProvisionedThroughput is not specified with BillingMode PAY_PER_REQUEST
###### CloudFormation Specifications
- Update Spec files to 2.24.0
- Update OnlyOne spec to have BlockDeviceMapping to include NoDevice with Ebs and VirtualName
- Add all the allowed values of the AWS::CloudFront::* Resources
- Add all the allowed values of the AWS::DAX::* Resources
###### Fixes
- Update config parsing to use the builtin Yaml decoder
- Add condition support for Inclusive [E2521](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E2521), Exclusive [E2520](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E2520), and AtLeastOne [E2522](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E2522) rules
- Update rule [E1029](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E1029) to better check Resource strings inside IAM Policies
- Improve the line/column information of a Match with array support


### 0.14.1
###### CloudFormation Specifications
- Update CloudFormation Specs to version 2.23.0
- Add allowed values for AWS::Config::* resources
- Add allowed values for AWS::ServiceDiscovery::* resources
- Fix allowed values for Apache MQ
###### Fixes
- Update rule [E3008](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3008) to not error when using a list from a custom resource
- Support simple types in the CloudFormation spec
- Add tests for the formatters

### 0.14.0
###### Features
- Add rule [E3035](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3035) to check the values of DeletionPolicy
- Add rule [E3036](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3036) to check the values of UpdateReplacePolicy
- Add rule [E2014](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E2014) to check that there are no REFs in the Parameter section
- Update rule [E2503](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E2503) to support TLS on NLBs
###### CloudFormation Specifications
- Update CloudFormation spec to version 2.22.0
- Add allowed values for AWS::Cognito::* resources
###### Fixes
- Update rule [E3002](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3002) to allow GetAtts to Custom Resources under a Condition

### 0.13.2
###### Features
- Introducing the cfn-lint logo!
- Update SAM dependency version
###### Fixes
- Fix CloudWatchAlarmComparisonOperator allowed values.
- Fix typo resoruce_type_spec in several files
- Better support for nested And, Or, and Not when processing Conditions

### 0.13.1
###### CloudFormation Specifications
- Add allowed values for AWS::CloudTrail::Trail resources
- Patch spec to have AWS::CodePipeline::CustomActionType Version included
###### Fixes
- Fix conditions logic to use AllowedValues when REFing a Parameter that has AllowedValues specified

### 0.13.0
###### Features
- New rule [W1011](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#W1011) to check if a FindInMap is using the correct map name and keys
- New rule [W1001](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#W1001) to check if a Ref/GetAtt to a resource that exists when Conditions are used
- Removed logic in [E1011](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E1011) and moved it to [W1011](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#W1011) for validating keys
- Add property relationships for AWS::ApplicationAutoScaling::ScalingPolicy into Inclusive, Exclusive, and AtLeastOne
- Update rule [E2505](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E2505) to check the netmask bit
- Include the ability to update the CloudFormation Specs using the Pricing API
###### CloudFormation Specifications
- Update to version 2.21.0
- Add allowed values for AWS::Budgets::Budget
- Add allowed values for AWS::CertificateManager resources
- Add allowed values for AWS::CodePipeline resources
- Add allowed values for AWS::CodeCommit resources
- Add allowed values for EC2 InstanceTypes from pricing API
- Add allowed values for RedShift InstanceTypes from pricing API
- Add allowed values for MQ InstanceTypes from pricing API
- Add allowed values for RDS InstanceTypes from pricing API
###### Fixes
- Fixed README indentation issue with .pre-commit-config.yaml
- Fixed rule [E2541](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E2541) to allow for multiple inputs/outputs in a CodeBuild task
- Fixed rule [E3020](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3020) to allow for a period or no period at the end of a ACM registration record
- Update rule [E3001](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3001) to support UpdateReplacePolicy
- Fix a cli issue where `--template` wouldn't be used when a .cfnlintrc was in the same folder
- Update rule [E3002](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3002) and [E1024](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#W3002) to support packaging of AWS::Lambda::LayerVersion content

### 0.12.1
###### CloudFormation Specifications
- Add AWS::WorkSpaces::Workspace.WorkspaceProperties ComputeTypeName, RunningMode allowed values
- Fix AWS::CloudWatch::Alarm to point Metrics at AWS::CloudWatch::Alarm.MetricDataQuery
###### Fixes
- Update rule [E1024](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E1024) to support Fn::Sub inside Fn::Cidr

### 0.12.0
###### Features
- Update rule [E1019](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E1019) to not allow for lists directly when doing a Ref or GetAtt to a list
- Move parameter checks from rule [E3030](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3030) to a new rule [W2030](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#W2030)
###### CloudFormation Specifications
- Updated to version 2.19.0
- Add S3 Bucket Allowed Values
- Add Route53 Allowed Values
- Add CodeDeploy Allowed Values
- Add AWS::SecretsManager::SecretTargetAttachment TargetType Allowed Values
- Add AWS::SES::ReceiptRule.Rule TlsPolicy Allowed Values
- Add AWS::AutoScaling::AutoScalingGroup, AWS::Route53::RecordSetGroup, and AWS::AutoScaling::AutoScalingGroup to OnlyOne
###### Fixes
- Improve [W7001](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#W7001) error message

### 0.11.1
###### CloudFormation Specifications
- Support Ref to IAM::Role or IAM::InstanceProfile with values looking for an ARN
- AWS::Batch::ComputeEnvironment InstanceRole is an InstanceProfile not Role
###### Fixes
- Add debug options to print a stack trace for rule E0002
- Update rule [E2015](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E2015) to include a try/catch around AllowedPattern testing to catch errors caused by non Python supported regex

### 0.11.0
###### Features
- Add rule [E3030](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3030) to use the newly patched spec to check resource properties values.  Update the following rules replaced by [E3030](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3030).
  - Delete rule [W2512](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#W2512)
  - Delete rule [E2531](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E2531)
  - Move allowed values check in rule [E2505](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E2505)
- Add rule [E3008](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3008) to use the newly patched spec to check a resource properties Ref and GetAtt.  Update the following rules replaced by [E3008](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3008).
  - Delete rule [E2502](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E2502)
  - Delete rule [W2505](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#W2505)
- Improve rule [E3020](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3020) to check MX records
###### CloudFormation Specifications
- Update CloudFormation specs to 2.18.1
- Append the CloudFormation spec to include:
  - AllowedValues for resource properties
  - Allowed Ref/GetAtts for resource properties
- Add specs for regions `eu-north-1`, `us-gov-east-1`, `us-gov-west-1`
- Add `AWS::StepFunctions::StateMachine` in all supported regions
- Add `AWS::CloudWatch::Alarm.Metric`, `AWS::CloudWatch::Alarm.MetricDataQuery` and `AWS::CloudWatch::Alarm.MetricStat` in all supported regions
- Add `AWS::Lambda::LayerVersion`, `AWS::Lambda::LayerVersion.Content`, and `AWS::Lambda::LayerVersionPermission` in all supported regions
###### Fixes
- Fix description on rule [W2501](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#W2501) to be more informative
- Update rule [E2532](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E2532) to allow `Parameters` in a `Task` in a Step Function
- Fix rule [E1010](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E1010) to allow Refs in the GetAtt attribute section
- Add `AWS::CloudFormation::Init` as an exception for rule E1029
- Add `Informational` error messages to JSON outputs
- Fix file searching `**/*` to recursively search in Python 3.5 and greater
- Update CopyRight from 2018 to 2019

### 0.10.2
###### Features
- Code coverage testing integrated into the CI process
- Update CloudFormation specs to 2.18.0
###### Fixes
- Fix rule [E2505](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E2505) to allow for SSM parameters when checking Cidr and Tenancy parameters
- Fix rule [E1029](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E1029) to not error on API Gateway stageVariables

### 0.10.1
###### Features
- Support stdin for reading and testing templates
###### Fixes
- Remove dependency on regex package as it requires gcc
- Remove rule [E3507](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3507) because it depends on regex package

### 0.10.0
###### Features
- Update specs to version 2.16.0
###### Fixes
- Require pathlib2 in Python versions earlier than 3.4.0
- Update aws-sam-translator to v1.8.0
- Update requests dependency to be at least version 2.15.0
- Add Python 3.7 support for Lambda
- Provide valid Python runtimes in rule [E2531](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E2531) error message
- Allow Fn::Sub inside a Fn::Sub for rule [E1019](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E1019)
- Add hardcoded list check as invalid in rule [E6003](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E6003)
- Fix home expansion with when looking for .cfnlintrc in Python 3.4
- Add testing in Travis for Py34, Py35, Py37
- Prevent spaces after the comma in spec file
- Update allowed Lambda Runtimes to include provided and ruby

### 0.9.2
###### Features
- Update specs to version 2.15.0
###### Fixes
- Fix rule [E3020](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3020) to allow multiple text records of up to 255 characters
- Fix rule [E3016](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3020) to handle conditions in Update Policies
- Fix rule [E2532](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E2532) to not fail when using a Fn::Sub and a number for a param

### 0.9.1
###### Features
- Add support for eu-west-3 and ap-northeast-3
- Add Resource Type AWS::CloudFormation::Macro to CloudFormation Spec
###### Fixes
- Fix the error message for YAML null being off by 1 line and 1 column number
- Add Custom Error for when trying to access an attribute in the classes that make up the template
- Fix an issue with deepcopy not creating copies with start and end marks
- Fix 4 rules that would fail when trying to create the path of the error and running into an integer
- Fix rule [E2015](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E2015) to force parameter default values to be a string when testing against the AllowedPattern regex pattern
- Fix a bug in the config engine in which append rules would have gone to override spec
- Remove exit calls from functions that are used in integrations preventing pre-mature failures
- Fix rule [E3002](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3002) [E3003](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3003) to support functions that may be able to support objects

### 0.9.0
###### Features
- Add rule [E8002](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E8002) to validate if resource Conditions or Fn::If conditions are defined
- Improve rule [E3002](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3002) to validate custom resources when custom specs are addended to the resource spec using override-spec
- Allow for configuration of cfn-lint using configuration files in the project and home folder called .cfnlintrc
- Updated specs to versions release 2.12.0
###### Fixes
- Fix rule [E3002](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3002) to not fail when looking for lists of objects and using a FindInMap or GetAtt to a custom resource as both could suppliy a list of objects
- Remove rule [E1025](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E1025) which was duplicative to the more extensive rule E8002
- Fix rule [E3020](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3020) to allow for quotes when checking the length
- Add generic exception handling to SAM transforming functions
- Complete redo how we handle arguments to fix issues created when linting multiple files with cfn-lint configurations in the file
- New CloudFormation spec patch to not require CidrBlock on resource type AWS::EC2::NetworkAclEntry
- New updates to AtLeastOne.json definition to require CidrBlock or Ipv6CidrBlock on resource type AWS::EC2::NetworkAclEntry
- A few documentation improvements

### 0.8.3
###### Features
- Add rule [E3022](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3022) to validate that there is only one SubnetRouteTableAssociation per subnet
###### Fixes
- Fix rule [E2502](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E2502) to check Arn and Name for AWS::EC2::LaunchTemplate resources
- Fix rule [E3016](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3016) to remove use of Path which may not be defined in certain scenarios
- Fix base rule Class so that resource_property_types and resource_sub_property_types is initialized from on every new rule and not copied from previous rules that were initialized
- Fix conversions of transformed templates in which keys stayed as str(s) instead of str_node(s)

### 0.8.2
###### Fixes
- Update rule [E2502](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E2502) to allow GetAtt against a nested stack or custom resource
- Update rules [E2541](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E2541) and [E2540](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E2540) to support conditions inside the CodePipeline
- Fix types in rule [E2532](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E2532) to now include InputPath and OutputPath
- Update rule [E1029](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E1029) to skip missing sub when looking at parameters in IAM policies
- Update rule [E2507](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E2507) to allow for strings in the IAM policy
- Update rule [E2507](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E2507) to allow the policy statement to be an object along with a list

### 0.8.1
###### Features
- Update Specs to the versions released October 19th, 2018
###### Fixes
- Fix rule [E2541](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E2541) to not fail on non-string values

### 0.8.0
###### Features
- Created a process to patch the CloudFormation Spec and patched a bunch of issues
- Support pre-commit hooks for linting templates
- Add rule [E3021](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3021) to that 5 or less targets are added to a CloudWatch Event
- Add rule [E1029](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E1029) to look for Sub variables that aren't inside a Sub
- Add rule [I3011](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#I3011) to validate that DynamDB Tables have deletion policy specified as the default is to delete the database.
- Add support for `info` errors
###### Fixes
- Update search_deep_keys to look for items in the Global section which is lost in a Transformation
- Clean up failures when loading files that are not yaml or json

### 0.7.4
###### Features
- Support parsing multiple files from the command line
- New rule [E3016](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3016) to validate a resources UpdatePolicy configuration
###### Fixes
- Removes sub parameter check from rule [E1012](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E1012). The same check is covered by
[E1019](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E1019)
- Fix rule [E1010](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E1010) when using a string not an array with Fn::Sub
- Fix rule [E3020](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3020) ignore intrinsic functions when checking values

### 0.7.3
###### Features
- Update the custom objects for the template to directly allow the calling of getting items and checking items that is condition safe
- Update CloudFormation Specs to 2018-09-21 released specs
###### Fixes
- Fix rule [E2540](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E2540) to not fail when the stage names aren't strings
- Fix rule [E3002](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3002) to not fail when processing Ref AWS::NoValue
- Core functionality updated to fail when extending rules directory doesn't exist
- Fix rule [E3002](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3002) metadata isn't supported as a resource property
- Fix rule [E2509](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E2509) to not error when using a function for description

### 0.7.2
###### Fixes
- Fix rule [W2501](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#W2501) to support dashes in KMS Key name
- Fix rule [E2543](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E2543) to not fail when the type of a step isn't known
- Fix rule [E2507](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E2507) to have an exception for ECR Policies.  Resource isn't required.
- Several Python cleanup items around initializing lists, how version is loaded, and dropping 'discover' in testing

### 0.7.1
###### Fixes
- Fix core decoding so the true error of a template parsing issue is visible to the user

### 0.7.0
###### Features
- New Rule [W1019](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#W1019) to make sure any Sub variables are used in the string
- New Rule [E2532](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E2532) to start basic validation of state machine syntax
- New Rule [W1020](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#W1020) to see if Sub is needed and variables are being used
- New Rule [E1028](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E1028) validate that first element in a Fn::If array is a string
- New Rule [W3002](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#W3002) to warn when templated templates are used
- Update Rule [E2507](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E2507) to check resource base policies
- Add Rule [W2511](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#W2511) to warn when using an older version of IAM Policy Version
###### Fixes
- Update Rule [E3002](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3002) to allow for templated code
- Update Rule [E1024](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E1024) to allow Cidr function to use GetAtt
- Fix core functionality to not error if the template is an array or string instead of an object

### 0.6.1
###### Fixes
- Fixes an issue where Template.get_values would return `Ref: AWS::NoValue`. This will no longer be returned as it is considered to be a Null value.

### 0.6.0
###### Features
- Update formatters to be similar from JSON and text outputs and modularize for easier growth later
- Don't raise an error with [E3020](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3020) when doing ACM DNS validation registration
- Add rule [E7003](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E7003) to validate that mapping keys are strings.  
- Add rule [E1027](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E1027) to validate that dynamic reference secure strings are to supported properties
- Add rule [E1004](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E1004) to validate that the Template Description is only a string
- Add rule [E6005](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E6005) to validate that an Output Description is only a string
- Add rule [E6012](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E6005) to validate that an Output Description is less than the maximum length
###### Fixes
- Fix core libraries to handle conditions around resource properties so that the resource and property checks still run
- Fix core libraries to handle the special property type `Tag` so that its checked when a rule is doing a Property Check

### 0.5.2
###### Fixes
- Support additional attributes in spec file for [E3002](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3003)
- Check custom resources as if they are 'AWS::CloudFormation::CustomResource' in rule [E3003](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3003)
- Fix [W6001](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#W6001) when an ImportValue is used to another function
- Fix [W2501](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#W2501) to support the new dynamic reference feature

### 0.5.1
###### Features
- Update rule [E3020](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3020) to support CAA and CNAME record checks
- Update specs to ones released on August 16, 2018

### 0.5.0
###### Features
- Load all instances of CloudFormationLintRule in a file. Class doesn't need to match the filename anymore
- Allow load yaml to accept a string allowing people to use cfn-lint as a module
- Add rule [W6001](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#W6001) to test outputs that are just using an import value
- Update specs to ones released on August 10, 2018
###### Fixes
- Update [E2507](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E2507) to support conditions and using get_values to test all condition paths
- Update [E2521](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E2521), [E2523](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E2523) to support conditions and using get_values to test all condition paths
- Rewrite [E2503](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E2503) to support intrinsic functions and conditions and lower case protocols
- Fix [E1018](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E1018) to support Sub inside a Split function
- Fix [E3003](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3003) description messages to be more informative
- Fix [E3001](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3001) to not require parameters when CreationPolicy is used
- Fix SAM region when no region is available from a local AWS profile or environment variable.

### 0.4.2
###### Features
- Update rule [E3020](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3020) to support AAAA record checks
###### Fixes
- Fix many rules that would fail if a sub parameter had a space at the beginning or end
- Fix crashing issues when trying to get resources that aren't properly configured

### 0.4.1
###### Features
- Update CloudFormation Specs to July 20th, 2018
###### Fixes
- Fix an issue with Exclusive resource properties and RDS with Snapshot and Password

### 0.4.0
###### Features
- Update CloudFormation specs to July 16th, 2018
- Support comma lists for regions, append rules, and ignore check parameters
- Added documentation explaining Resource Specification based rules
###### Fixes
- Fix a bunch of typos across many different rules
- Support DeepCopy with Template and custom String classes used for marking up templates
- Fix Rule [E3002](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3002) to support CommaDelimitedList when looking for List Parameters
- Fix core engine to check that something is a Dict instead of assuming it is

### 0.3.5
###### Features
- Update CloudFormation Specs to July 12th, 2018
- Rule [E7012](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E7012) added to check the limits of attributes in a Mapping
- Rule [E2012](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E2012) added to check maximum size of a parameter value
- Rule [E1003](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E1003) added to check the maximum length of the template Description
- Guide created to help new users write new rules
###### Fixes
- Catch KeyError when trying to discover the line and column number of an error
- Update Lambda rules to support dotnet core
- Fix rule [E1017](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E1017) so we unpack first element of select as a dict
- Fix rule [E1024](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E1024) to support ImportValue and appropriately checking number for the last element

### 0.3.3
###### Features
- Support for Yaml C Parser when available.
- Catch rule processing errors and raise a lint error in their place.
- Add rules for the limit on Parameter, Mapping, Resource and Output names
- Add Rule [W3005](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#W3005) to warn for when DependsOn is specified but not needed
- Add Rule [E2509](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E2509) to check if Security Group Descriptions are properly configured
- Add `source_url` to rules so rule reference documentation can be provided
###### Fixes
- Fixed issues when Conditions had lists for values
- Fixed issue where underscore was allowed for AlphaNumeric names

### 0.3.2
###### Features
- Try/Catch added to rule processing so code failures in rules won't crash cfn-lint
- Parse YAML files using C parser when available.  Greatly speeds up YAML parsing.
###### Fixes
- Template class updated to handle conditions where lists are in the true/false values
- Fix regex for checking Resource, Output, etc. names to not include underscore

### 0.3.1
###### Features
- Update rule [E3020](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3020) to validate A recordsets
###### Fixes
- Require "aws-sam-translator" dependency be at least 1.6.0
- Add support for wildcards in rule [E3013](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3013) - Support conditions in Lists for rule [E3002](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3002) - Include filename when we run into Null and Duplicate values when parsing yaml
- Rule W2510 now allows for AllowedValues instead of just Min/MaxValue for compliance of Lambda MemorySize
- Rule [E2530](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E2530) updated to checked AllowedValues for compliance of Lambda MemorySize

### 0.3.0
###### Features
- Serverless Transforms now handled by SAM libraries
- Add Rule [E2508](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E2508): Add checks for IAM
  - Managed Policies attached to IAM user, group or role can't be more than 10
  - An IAM user can be a member of no more than 10 groups
  - There can only be 1 role in an instance profile
  - AssumeRolePolicyDocument size is less than <2048 characters
- Add Rule [E1002](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E1002): Check overall template size to make sure its below
- Add Rule [E3013](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3013): CloudFront aliases should contain valid domain names
- Add Rule [E3020](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3020): Check if all RecordSets are correctly configured
  - Strings end and start with double quotes
  - Size is less than 256 characters
  - Record Types are within the specification
- Short hand parameter switches and no longer need --template
###### Fixes
- Don't report a Condition not being used if it is used by another Condition

### 0.2.2
###### Fixes
- Fixed issues with Yaml and Json parsing for complex strings in Python 2.7
- Added eu-central-1 Availability Zones to acceptable AZ list
- Added nodejs8.10 to supported Lambda
- Added Version as an attribute for a Custom Resource
- Parseable output is now colon(:) delimited

### 0.2.1
###### Features
- Added AllowedValues for Cidr parameter checking Rule W2509
- Add Rule [E2004](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E2004) to check Allowed values for Cidr parameters are a valid Cidr range
- Disable mapping Name checks [W7001](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#W7001) if dynamic mapping names are used (Ref, FindInMap)
- New Rule [E1026](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E1026) to make sure Ref's in 'Conditions' are to parameters and not resources
- Updated CloudFormation specs to June 5th, 2018
###### Fixes
- Fixed an issue with Rule [E1019](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E1019) not giving errors when there was a bad pseudo parameter
- Fixed an issue where conditions with Refs were validated as strings instead of Refs
- Fix crash errors when an empty yaml file is provided
- Updated condition functions to return the full object (Ref isn't translated while looking for AWS::NoValue)
- Support Map Type properties when doing PrimitiveType check [E3012](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3012) - Fix an issue when boolean values not being checked when using check_value

### 0.2.0
###### Features
- Standard cfn-lint Errors ([E0000](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E0000)) for null, duplicate, and parse errors
- Add a new check for CloudFormation limits
- Add a new check for Parameter, Resource, Output, and Mapping names
- Update specs to those released on May 25th, 2018
- Strong type checking for property values result in Errors ([E3012](https://github.com/aws-cloudformation/cfn-python-lint/blob/master/docs/rules.md#E3012))
###### Fixes
- Transform logic updated to not add a Role if one is specified for a serverless function
- Fixed logic around Fn::If when the result is an object
- Fix conditions when checking property value structure

### 0.1.0
###### Features
- Update CloudFormation specs to include recent releases
- Add checks for duplicate resource names
- Add checks for null values in templates
- Add support in Circular Dependency checks to go multiple levels deep
- Add check for unused mappings
- Add check for unused and not found conditions
- Convert Errors to Warnings that don't cause a failure when implementing a template
###### Fixes
- Fix check for cfn-lint configurations in templates
- Fix Sub Functions checks failing on sub stacks or custom resources
- Fix Serverless Transforms not failing when trying to create multiple RestApiIds
- Fix TOX encoding issues with certain JSON files
- Update Lambda Memory size to 3008
- Fix FindInMap failing when the first parameter is also FindInMap
- Fix key search function to appropriately respond to nested finds (FindInMap inside a FindInMap)

### 0.0.10
###### Features
- Capability to merge and modify the CloudFormation spec with provided JSON
  - Allows for changing what properties are required
  - Can change what resource types are allowed
- Remove warnings that were in error checks to keep errors focused on issues preventing success
- Improve circular dependency checks to go multiple levels deep
- Check null and duplicate values in JSON and YAML templates
###### Fixes
- Some primitive type properties were not getting checked
- Include support for Long as a number based check
- Improve get condition values to support more complex scenarios

### 0.0.8
###### Features
- Added a rule to check for only one resource property in a set
- Added a rule for more than one of resource properties in a set
- Added a rule for mutually exclusive resource properties

###### Fixes
- Support parsing JSON files that have tabs
- Better error handling for when a property is a list instead of an object
- Error handling for when files can't be read or don't exist

### 0.0.7
###### Features
- Fix for supporting more parameter types when checking REFs to parameters for Security Groups

### 0.0.6
###### Features
- Exit code non zero on errors or warnings

### 0.0.5
###### Features
- Testing CloudFormation resources against the Resource Spec
- Test Functions against supported included functions
- Test overall CloudFormation structure
- Test Regionalization of a template against the Resource Spec
- Ability to add additional rules on parameter
- In depth checks of values around AWS::EC2::VPC, AWS::EC2::Subnet, and AWS::EC2::SecurityGroup
