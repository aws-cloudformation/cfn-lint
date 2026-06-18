crate::extension_schema_rule!(
    E3029,
    id: "E3029",
    description: "Validate Route53 record set aliases",
    severity: crate::rules::Severity::Error,
    resource_type: "AWS::Route53::RecordSet",
    schema_path: "../../../../data/schemas/extensions/aws_route53_recordset/recordset_alias.json",
    regional: false
);
