# Rules

### Errors
Errors will start with the letter `E`. Errors will result in a hard failure for the template being validated.

### Warnings
Warnings start with the letter `W`. Warnings alert you when the template doesnt follow best practices but should still function.  *Example: If you use a parameter for a RDS master password you should have the parameter property NoEcho set to true.*


## Categories

| Rule Numbers    | Category |
| --------------- | ------------- |
| (E&#124;W)0XXX  | Basic Template Errors. Examples: Not parseable, main sections (Outputs, Resources, etc.)  |
| (E&#124;W)1XXX  | Functions (Ref, GetAtt, etc.)  |
| (E&#124;W)2XXX  | Parameters |
| (E&#124;W)3XXX  | Resources |
| (E&#124;W)4XXX  | Metadata |
| (E&#124;W)6xxx  | Outputs |
| (E&#124;W)7xxx  | Mappings |
| (E&#124;W)8xxx  | Conditions |
| (E&#124;W)9xxx  | Reserved for users rules |


*Warning*
Rule `E3012` is used to check the types for value of a resource property.  A number is a number, string is a string, etc.  There are occasions where this could be just a warning and other times it could be an error.  cfn-lint doesn't have an exception process so all instances of this issue are considered errors. You can disable this rule using `--ignore-checks` if it is not required for your internal best practices.


## Rules
THe following **67** rules are applied by this linter:

| Rule ID  | Title | Description | Tags |
| -------- | ----- | ----------- |----- |
| E1001 | Basic CloudFormation Template Configuration | Making sure the basic CloudFormation template componets are propery configured | `base` |
| E1010 | GetAtt validation of parameters | Making sure the function GetAtt is of list | `base`,`functions`,`getatt` |
| E1011 | FindInMap validation of configuration | Making sure the function is a list of appropriate config | `base`,`functions`,`getatt` |
| E1012 | Check if Refs exist | Making sure the refs exist | `base`,`functions`,`ref` |
| E1015 | GetAz validation of parameters | Making sure the function not is of list | `base`,`functions`,`getaz` |
| E1016 | ImportValue validation of parameters | Making sure the function not is of list | `base`,`functions`,`importvalue` |
| E1017 | Select validation of parameters | Making sure the function not is of list | `base`,`functions`,`select` |
| E1018 | Split validation of parameters | Making sure the split function is properly configured | `base`,`functions`,`split` |
| E1019 | Sub validation of parameters | Making sure the split function is properly configured | `base`,`functions`,`sub` |
| E1020 | Ref validation of value | Making the Ref has a value of String (no other functions are supported) | `base`,`functions`,`ref` |
| E1021 | Base64 validation of parameters | Making sure the function not is of list | `base`,`functions`,`base64` |
| E1022 | Join validation of parameters | Making sure the join function is properly configured | `base`,`functions`,`join` |
| E1023 | Validation NOT function configuration | Making sure that NOT functions are list | `base`,`functions`,`not` |
| E1024 | Cidr validation of parameters | Making sure the function CIDR is a list with valid values | `base`,`functions`,`cidr` |
| E1025 | Check if Conditions exist | Making sure the Conditions used in Fn:If functions exist | `base`,`functions`,`if` |
| E1026 | Cannot reference resources in the Conditions block of the template | Check that any Refs in the Conditions block uses no resources | `base`,`functions`,`ref` |
| E2001 | Parameters have appropriate properties | Making sure the parameters are properly configured | `base`,`parameters` |
| E2002 | Parameters have appropriate type | Making sure the parameters have a correct type | `base`,`parameters` |
| E2003 | Parameters have appropriate names | Check if Parameters are properly named (A-Za-z0-9) | `base`,`parameters` |
| E2004 | CIDR Allowed Values should be a Cidr Range | Check if a parameter is being used as a CIDR. If it is make sure allowed values are proper CIDRs | `base`,`parameters`,`cidr` |
| E2010 | Parameter limit not exceeded | Check the number of Parameters in the template is lessthan the upper limit | `base`,`parameters`,`limits` |
| E2502 | Check if IamInstanceProfile are using the name and not ARN | See if there are any properties IamInstanceProfileare using name and not ARN | `base`,`properties` |
| E2503 | Resource ELB Properties | See if Elb Resource Properties are set correctly HTTPS has certificate HTTP has no certificate | `base`,`properties`,`elb` |
| E2504 | Check Ec2 Ebs Properties | See if Ec2 Eb2 Properties are valid | `base`,`properties`,`ec2`,`ebs` |
| E2505 | Resource EC2 VPC Properties | See if EC2 VPC Properties are set correctly | `base`,`properties`,`vpc` |
| E2506 | Resource EC2 Security Group Ingress Properties | See if EC2 Security Group Ingress Properties are set correctly. Check that "SourceSecurityGroupId" or "SourceSecurityGroupName" are  are exclusive and using the type of Ref or GetAtt  | `base`,`resources`,`securitygroup` |
| E2507 | Check if IAM Policies are properly configured | See if there elements inside an IAM policy are correct | `base`,`properties`,`iam` |
| E2510 | Resource EC2 PropertiesEc2Subnet Properties | See if EC2 Subnet Properties are set correctly | `base`,`properties`,`subnet` |
| E2520 | Check Properties that are mutually exclusive | Making sure CloudFormation properties that are exclusive are not defined | `base`,`resources` |
| E2521 | Check Properties that are required together | Make sure CloudFormation resource properties are included together when required | `base`,`resources` |
| E2522 | Check Properties that need at least one of a list of properties | Making sure CloudFormation properties that require at least one property from a list. More than one can be included. | `base`,`resources` |
| E2523 | Check Properties that need only one of a list of properties | Making sure CloudFormation properties that require only one property from a list. One has to be specified. | `base`,`resources` |
| E2530 | Check Lambda Memory Size Properties | See if Lambda Memory Size is valid | `base`,`resources`,`lambda` |
| E2531 | Check Lambda Runtime Properties | See if Lambda Runtime is in valid | `base`,`resources`,`lambda` |
| E2540 | CodePipeline Stages | See if CodePipeline stages are set correctly | `base`,`properties`,`codepipeline` |
| E2541 | CodePipeline Stage Actions | See if CodePipeline stage actions are set correctly | `base`,`resources`,`codepipeline` |
| E3001 | Basic CloudFormation Resource Check | Making sure the basic CloudFormation resources are propery configured | `base`,`resources` |
| E3002 | Resource properties are valid | Making sure that resources properties are propery configured | `base`,`resources` |
| E3003 | Required Resource Parameters are missing | Making sure that Resources properties that are required exist | `base`,`resources` |
| E3004 | Resource dependencies are not circular | Check that Resources are not circularly dependent by Ref, Sub, or GetAtt | `base`,`resources`,`circularly` |
| E3005 | Check DependsOn values for Resources | Check that the DependsOn values are valid | `base`,`resources`,`dependson` |
| E3006 | Resources have appropriate names | Check if Resources are properly named (A-Za-z0-9) | `base`,`resources` |
| E3010 | Resource limit not exceeded | Check the number of Resources in the template is lessthan the upper limit | `base`,`resources`,`limits` |
| E3012 | Check resource properties values | Checks resource property values with Primitive Types for values that match those types. | `base`,`resources` |
| E4001 | Metadata Interface have appropriate properties | Metadata Interface properties are properly configured | `base`,`metadata` |
| E6001 | Outputs have appropriate properties | Making sure the outputs are properly configured | `base`,`outputs` |
| E6002 | Outputs have required properties | Making sure the outputs have required properties | `base`,`outputs` |
| E6003 | Outputs have values of strings | Making sure the outputs have strings as values | `base`,`outputs` |
| E6004 | Outputs have appropriate names | Check if Outputs are properly named (A-Za-z0-9) | `base`,`outputs` |
| E6010 | Output limit not exceeded | Check the number of Outputs in the template is lessthan the upper limit | `base`,`outputs`,`limits` |
| E7001 | Mappings are appropriately configured | Check if Mappings are properly configured | `base`,`mappings` |
| E7002 | Mappings have appropriate names | Check if Mappings are properly named (A-Za-z0-9) | `base`,`mapping` |
| E7010 | Mapping limit not exceeded | Check the number of Mappings in the template is lessthan the upper limit | `base`,`mappings`,`limits` |
| E8001 | Conditions have appropriate properties | Check if Conditions are properly configured | `base`,`conditions` |
| W2001 | Check if Parameters are Used | Making sure the parameters defined are used | `base`,`parameters` |
| W2501 | Check if Password Properties are correctly configured | Password properties should be strings and if parameter using NoEcho | `base`,`parameters`,`passwords` |
| W2505 | Check if VpcID Parameters have the correct type | See if there are any refs for VpcId to a parameter of innapropriate type.  Appropriate Types are [AWS::EC2::VPC::Id, AWS::SSM::Parameter::Value<AWS::EC2::VPC::Id>] | `base`,`parameters`,`vpcid` |
| W2506 | Check if ImageId Parameters have the correct type | See if there are any refs for ImageId to a parameter of innapropriate type. Appropriate Types are [AWS::EC2::Image::Id, AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>] | `base`,`parameters`,`imageid` |
| W2507 | Security Group Parameters are of correct type AWS::EC2::SecurityGroup::Id | Check if a parameter is being used in a resource for Security Group.  If it is make sure it is of type AWS::EC2::SecurityGroup::Id | `base`,`parameters`,`securitygroup` |
| W2508 | Availability Zone Parameters are of correct type AWS::EC2::AvailabilityZone::Name | Check if a parameter is being used in a resource for Security Group.  If it is make sure it is of type AWS::EC2::AvailabilityZone::Name | `base`,`parameters`,`availabilityzone` |
| W2509 | CIDR Parameters have allowed values | Check if a parameter is being used as a CIDR. If it is make sure it has allowed values regex comparisons | `base`,`parameters`,`availabilityzone` |
| W2510 | Parameter Memory Size attributes should have max and min | Check if a parameter that is used for Lambda memory size  should have a min and max size that matches Lambda constraints | `base`,`parameters`,`lambda` |
| W2512 | Parameter Lambda Runtime has allowed values set | Check if a parameter that is used for Lambda runtime  has allowed values constraint defined | `base`,`parameters`,`lambda` |
| W3010 | Availability Zone Parameters should not be hardcoded | Check if an Availability Zone property is hardcoded. | `base`,`parameters`,`availabilityzone` |
| W4001 | Metadata Interface parameters exist | Metadata Interface parameters actually exist | `base`,`metadata` |
| W7001 | Check if Mappings are Used | Making sure the mappings defined are used | `base`,`conditions` |
| W8001 | Check if Conditions are Used | Making sure the conditions defined are used | `base`,`conditions` |
