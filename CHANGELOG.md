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

### 0.2.0
###### Features
- Standard cfn-lint Errors (E0000) for null, duplicate, and parse errors
- Add a new check for CloudFormation limits
- Add a new check for Parameter, Resource, Output, and Mapping names
- Update specs to those released on May 25th, 2018
- Strong type checking for property values result in Errors (E3012)
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
