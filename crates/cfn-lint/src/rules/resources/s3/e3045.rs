crate::extension_schema_rule!(
    E3045,
    id: "E3045",
    description: "Validate AccessControl are set with OwnershipControls",
    severity: crate::rules::Severity::Error,
    resource_type: "AWS::S3::Bucket",
    schema_path: "../../../../data/schemas/extensions/aws_s3_bucket/ownershipcontrols.json",
    regional: false
);
