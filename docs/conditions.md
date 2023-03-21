# Conditions

Conditions allow a template developer to create many scenarios using the same template. cfn-lint does not use parameter values to determine the validaty of a template so cfn-lint will try to validate all the possible scenarios that are created by using conditions.

# Using conditions

## Defining conditions

Conditions are defined in a section of your CloudFormation template. At the lowest level all conditions will equate to a set of `Fn::Equals` that compares two values. Advanced condition scenarios can be created using `Fn::And`, `Fn::Or`, `Fn::Not`. Conditions can be nested using `Fn::Condition` function.

```yaml
Parameters:
    Environment:
        Type: String
Conditions:
    IsProduction: !Equals [!Ref Environment, "prod"]
    IsDevelopment: !Equals [!Ref Environment, "dev"]
    IsProductionAndUsEast1:
        !And
        - !Condition IsProduction
        - !Equals [!Ref AWS::Region, "us-east-1"]
```

## Using conditions

Conditions can be used in two locations. 1/ Is the at the resource or output level defined by the attribute `Condition` 2/ Using the function `Fn::If` under a resources `Properties` property. `Fn::If` can be used at any layer as long as it is the only key in an object.

```yaml
Resources:
    HTTPSCertificate:
        Type: AWS::CertificateManager::Certificate
        Condition: HaveTargets
        Properties:
            DomainName: 'example.com'
            ValidationMethod: DNS

    CloudFrontAlias:
        Type: AWS::Route53::RecordSet
        Condition: CreateDNSRecords
        Properties:
            HostedZoneId: !Ref ServiceHostedZoneId
            Name: 'example.com'
            Type: A
            AliasTarget:
                DNSName: !GetAtt Distribution1.DomainName
                HostedZoneId: Z2FDTNDATAQYW2

    Distribution1:
        Type: AWS::CloudFront::Distribution
        Condition: HaveTargets
        Properties:
            DistributionConfig:
                Enabled: true
                ViewerCertificate:
                    AcmCertificateArn: !Ref HTTPSCertificate
                    SslSupportMethod: sni-only
                    MinimumProtocolVersion: TLSv1.2_2019
                DefaultCacheBehavior:
                    TargetOriginId: Service1
Outputs:
    DomainName:
        Value: !If [HaveTargets, !GetAtt Distribution1.DomainName, ""]
```


# Handling conditions

## SymPy
[SymPy](https://docs.sympy.org/) is a python package that allows you to build formulas and calculate if a scenario is a legitimate scenario. For instance cfn-lint will build a solver for conditions `IsProduction` and `IsDevelopment` that will calculate the following possibilites `True`/`False`, `False`/`True`, or `False`/`False`. To build a solver cfn-lint will build formulas accordingly `Fn::And` is converted to `And`, `Fn::Or` is converted to `Or`, and `Fn::Not` is converted to `Not`. It will understand `Fn::Equals` that use the same parameter and create a `Not(And(...))` formula that will make sure that the equals in the `And` are no never `True` together.
