### Roadmap
- Be able to test transforms (include)
- Add tests around common resource types
  - AutoScaling
  - Ec2 Instances
  - Load Balancers
  - RDS
- Create a framework to test ARNs
- Test Ref resources to IAM Roles have good assume role documents.  Example: Lambda Function Ref refers to an IAM Role that can be assume by Lambda.
- More Warnings around hard coded values (Regions, AccountIds) to help with the practice of reusability

### 0.7.2
###### Fixes
- Fix rule [W2501](https://github.com/awslabs/cfn-python-lint/blob/master/docs/rules.md#W2501) to support dashes in KMS Key name
- Fix rule [E2543](https://github.com/awslabs/cfn-python-lint/blob/master/docs/rules.md#E2543) to not fail when the type of a step isn't known
- Fix rule [E2507](https://github.com/awslabs/cfn-python-lint/blob/master/docs/rules.md#E2507) to have an exception for ECR Policies.  Resource isn't required.
- Several Python cleanup items around initializing lists, how version is loaded, and dropping 'discover' in testing

### 0.7.1
###### Fixes
- Fix core decoding so the true error of a template parsing issue is visible to the user

### 0.7.0
###### Features
- New Rule [W1019](https://github.com/awslabs/cfn-python-lint/blob/master/docs/rules.md#W1019) to make sure any Sub variables are used in the string
- New Rule [E2532](https://github.com/awslabs/cfn-python-lint/blob/master/docs/rules.md#E2532) to start basic validation of state machine syntax
- New Rule [W1020](https://github.com/awslabs/cfn-python-lint/blob/master/docs/rules.md#W1020) to see if Sub is needed and variables are being used
- New Rule [E1028](https://github.com/awslabs/cfn-python-lint/blob/master/docs/rules.md#E1028) validate that first element in a Fn::If array is a string
- New Rule [W3002](https://github.com/awslabs/cfn-python-lint/blob/master/docs/rules.md#W3002) to warn when templated templates are used
- Update Rule [E2507](https://github.com/awslabs/cfn-python-lint/blob/master/docs/rules.md#E2507) to check resource base policies
- Add Rule [W2511](https://github.com/awslabs/cfn-python-lint/blob/master/docs/rules.md#W2511) to warn when using an older version of IAM Policy Version
###### Fixes
- Update Rule [E3002](https://github.com/awslabs/cfn-python-lint/blob/master/docs/rules.md#E3002) to allow for templated code
- Update Rule [E1024](https://github.com/awslabs/cfn-python-lint/blob/master/docs/rules.md#E1024) to allow Cidr function to use GetAtt
- Fix core functionality to not error if the template is an array or string instead of an object

### 0.6.1
###### Fixes
- Fixes an issue where Template.get_values would return `Ref: AWS::NoValue`. This will no longer be returned as it is considered to be a Null value.

### 0.6.0
###### Features
- Update formatters to be similar from JSON and text outputs and modularize for easier growth later
- Don't raise an error with [E3020](https://github.com/awslabs/cfn-python-lint/blob/master/docs/rules.md#E3020) when doing ACM DNS validation registration
- Add rule [E7003](https://github.com/awslabs/cfn-python-lint/blob/master/docs/rules.md#E7003) to validate that mapping keys are strings.  
- Add rule [E1027](https://github.com/awslabs/cfn-python-lint/blob/master/docs/rules.md#E1027) to validate that dynamic reference secure strings are to supported properties
- Add rule [E1004](https://github.com/awslabs/cfn-python-lint/blob/master/docs/rules.md#E1004) to validate that the Template Description is only a string
- Add rule [E6005](https://github.com/awslabs/cfn-python-lint/blob/master/docs/rules.md#E6005) to validate that an Output Description is only a string
- Add rule [E6012](https://github.com/awslabs/cfn-python-lint/blob/master/docs/rules.md#E6005) to validate that an Output Description is less than the maximum length
###### Fixes
- Fix core libraries to handle conditions around resource properties so that the resource and property checks still run
- Fix core libraries to handle the special property type `Tag` so that its checked when a rule is doing a Property Check

### 0.5.2
###### Fixes
- Support additional attributes in spec file for [E3002](https://github.com/awslabs/cfn-python-lint/blob/master/docs/rules.md#E3003)
- Check custom resources as if they are 'AWS::CloudFormation::CustomResource' in rule [E3003](https://github.com/awslabs/cfn-python-lint/blob/master/docs/rules.md#E3003)
- Fix [W6001](https://github.com/awslabs/cfn-python-lint/blob/master/docs/rules.md#W6001) when an ImportValue is used to another function
- Fix [W2501](https://github.com/awslabs/cfn-python-lint/blob/master/docs/rules.md#W2501) to support the new dynamic reference feature

### 0.5.1
###### Features
- Update rule [E3020](https://github.com/awslabs/cfn-python-lint/blob/master/docs/rules.md#E3020) to support CAA and CNAME record checks
- Update specs to ones released on August 16, 2018

### 0.5.0
###### Features
- Load all instances of CloudFormationLintRule in a file. Class doesn't need to match the filename anymore
- Allow load yaml to accept a string allowing people to use cfn-lint as a module
- Add rule [W6001](https://github.com/awslabs/cfn-python-lint/blob/master/docs/rules.md#W6001) to test outputs that are just using an import value
- Update specs to ones released on August 10, 2018
###### Fixes
- Update [E2507](https://github.com/awslabs/cfn-python-lint/blob/master/docs/rules.md#E2507) to support conditions and using get_values to test all condition paths
- Update [E2521](https://github.com/awslabs/cfn-python-lint/blob/master/docs/rules.md#E2521), [E2523](https://github.com/awslabs/cfn-python-lint/blob/master/docs/rules.md#E2523) to support conditions and using get_values to test all condition paths
- Rewrite [E2503](https://github.com/awslabs/cfn-python-lint/blob/master/docs/rules.md#E2503) to support intrinsic functions and conditions and lower case protocols
- Fix [E1018](https://github.com/awslabs/cfn-python-lint/blob/master/docs/rules.md#E1018) to support Sub inside a Split function
- Fix [E3003](https://github.com/awslabs/cfn-python-lint/blob/master/docs/rules.md#E3003) description messages to be more informative
- Fix [E3001](https://github.com/awslabs/cfn-python-lint/blob/master/docs/rules.md#E3001) to not require parameters when CreationPolicy is used
- Fix SAM region when no region is available from a local AWS profile or environment variable.

### 0.4.2
###### Features
- Update rule [E3020](https://github.com/awslabs/cfn-python-lint/blob/master/docs/rules.md#E3020) to support AAAA record checks
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
- Fix Rule [E3002](https://github.com/awslabs/cfn-python-lint/blob/master/docs/rules.md#E3002) to support CommaDelimitedList when looking for List Parameters
- Fix core engine to check that something is a Dict instead of assuming it is

### 0.3.5
###### Features
- Update CloudFormation Specs to July 12th, 2018
- Rule [E7012](https://github.com/awslabs/cfn-python-lint/blob/master/docs/rules.md#E7012) added to check the limits of attributes in a Mapping
- Rule [E2012](https://github.com/awslabs/cfn-python-lint/blob/master/docs/rules.md#E2012) added to check maximum size of a parameter value
- Rule [E1003](https://github.com/awslabs/cfn-python-lint/blob/master/docs/rules.md#E1003) added to check the maximum length of the template Description
- Guide created to help new users write new rules
###### Fixes
- Catch KeyError when trying to discover the line and column number of an error
- Update Lambda rules to support dotnet core
- Fix rule [E1017](https://github.com/awslabs/cfn-python-lint/blob/master/docs/rules.md#E1017) so we unpack first element of select as a dict
- Fix rule [E1024](https://github.com/awslabs/cfn-python-lint/blob/master/docs/rules.md#E1024) to support ImportValue and appropriately checking number for the last element

### 0.3.3
###### Features
- Support for Yaml C Parser when available.
- Catch rule processing errors and raise a lint error in their place.
- Add rules for the limit on Parameter, Mapping, Resource and Output names
- Add Rule [W3005](https://github.com/awslabs/cfn-python-lint/blob/master/docs/rules.md#W3005) to warn for when DependsOn is specified but not needed
- Add Rule [E2509](https://github.com/awslabs/cfn-python-lint/blob/master/docs/rules.md#E2509) to check if Security Group Descriptions are properly configured
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
- Update rule [E3020](https://github.com/awslabs/cfn-python-lint/blob/master/docs/rules.md#E3020) to validate A recordsets
###### Fixes
- Require "aws-sam-translator" dependency be at least 1.6.0
- Add support for wildcards in rule [E3013](https://github.com/awslabs/cfn-python-lint/blob/master/docs/rules.md#E3013) - Support conditions in Lists for rule [E3002](https://github.com/awslabs/cfn-python-lint/blob/master/docs/rules.md#E3002) - Include filename when we run into Null and Duplicate values when parsing yaml
- Rule W2510 now allows for AllowedValues instead of just Min/MaxValue for compliance of Lambda MemorySize
- Rule [E2530](https://github.com/awslabs/cfn-python-lint/blob/master/docs/rules.md#E2530) updated to checked AllowedValues for compliance of Lambda MemorySize

### 0.3.0
###### Features
- Serverless Transforms now handled by SAM libraries
- Add Rule [E2508](https://github.com/awslabs/cfn-python-lint/blob/master/docs/rules.md#E2508): Add checks for IAM
  - Managed Policies attached to IAM user, group or role can't be more than 10
  - An IAM user can be a member of no more than 10 groups
  - There can only be 1 role in an instance profile
  - AssumeRolePolicyDocument size is less than <2048 characters
- Add Rule [E1002](https://github.com/awslabs/cfn-python-lint/blob/master/docs/rules.md#E1002): Check overall template size to make sure its below
- Add Rule [E3013](https://github.com/awslabs/cfn-python-lint/blob/master/docs/rules.md#E3013): CloudFront aliases should contain valid domain names
- Add Rule [E3020](https://github.com/awslabs/cfn-python-lint/blob/master/docs/rules.md#E3020): Check if all RecordSets are correctly configured
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
- Add Rule [E2004](https://github.com/awslabs/cfn-python-lint/blob/master/docs/rules.md#E2004) to check Allowed values for Cidr parameters are a valid Cidr range
- Disable mapping Name checks [W7001](https://github.com/awslabs/cfn-python-lint/blob/master/docs/rules.md#W7001) if dynamic mapping names are used (Ref, FindInMap)
- New Rule [E1026](https://github.com/awslabs/cfn-python-lint/blob/master/docs/rules.md#E1026) to make sure Ref's in 'Conditions' are to parameters and not resources
- Updated CloudFormation specs to June 5th, 2018
###### Fixes
- Fixed an issue with Rule [E1019](https://github.com/awslabs/cfn-python-lint/blob/master/docs/rules.md#E1019) not giving errors when there was a bad pseudo parameter
- Fixed an issue where conditions with Refs were validated as strings instead of Refs
- Fix crash errors when an empty yaml file is provided
- Updated condition functions to return the full object (Ref isn't translated while looking for AWS::NoValue)
- Support Map Type properties when doing PrimitiveType check [E3012](https://github.com/awslabs/cfn-python-lint/blob/master/docs/rules.md#E3012) - Fix an issue when boolean values not being checked when using check_value

### 0.2.0
###### Features
- Standard cfn-lint Errors ([E0000](https://github.com/awslabs/cfn-python-lint/blob/master/docs/rules.md#E0000)) for null, duplicate, and parse errors
- Add a new check for CloudFormation limits
- Add a new check for Parameter, Resource, Output, and Mapping names
- Update specs to those released on May 25th, 2018
- Strong type checking for property values result in Errors ([E3012](https://github.com/awslabs/cfn-python-lint/blob/master/docs/rules.md#E3012))
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
