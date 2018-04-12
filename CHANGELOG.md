### Roadmap
- Be able to test transforms (serverless, include)
- Add tests around common resource types
  - AutoScaling
  - Ec2 Instances
  - Load Balancers
  - RDS
- Create a framework to test ARNs
- Test Ref resources to IAM Roles have good assume role documents.  Example: Lambda Function Ref refers to an IAM Role that can be assume by Lambda.
- More Warnings around hard coded values (Regions, AccountIds) to help with the practice of reusability

### 0.1.0
###### Features
- Testing CloudFormation resources against the Resource Spec
- Test Functions against supported included functions
- Test overall CloudFormation structure
- Test Regionalization of a template against the Resource Spec
- Ability to add additional rules on parameter
- In depth checks of values around AWS::EC2::VPC, AWS::EC2::Subnet, and AWS::EC2::SecurityGroup
