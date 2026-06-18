//! GetAtt attribute resolution from CloudFormation provider schemas.
//!
//! Determines which attributes are valid for `Fn::GetAtt` based on:
//! - `readOnlyProperties` in the schema (default)
//! - All properties for types in `ALL_PROPERTY_TYPES`
//! - Wildcard for custom/serverless/module types
//! - Additional attributes from `EXCEPTIONS`

/// Resource types that expose ALL their properties as GetAtt attributes.
static ALL_PROPERTY_TYPES: &[&str] = &[
    "AWS::Amplify::Branch",
    "AWS::Amplify::Domain",
    "AWS::AppSync::DomainName",
    "AWS::AppSync::FunctionConfiguration",
    "AWS::AppSync::Resolver",
    "AWS::AutoScaling::AutoScalingGroup",
    "AWS::Backup::BackupSelection",
    "AWS::Backup::BackupVault",
    "AWS::CodeArtifact::Domain",
    "AWS::CodeArtifact::Repository",
    "AWS::EC2::CapacityReservation",
    "AWS::EC2::Instance",
    "AWS::EC2::SecurityGroup",
    "AWS::EC2::Subnet",
    "AWS::EC2::VPC",
    "AWS::EFS::MountTarget",
    "AWS::EKS::Nodegroup",
    "AWS::ElasticLoadBalancingV2::LoadBalancer",
    "AWS::Events::EventBus",
    "AWS::EventSchemas::Discoverer",
    "AWS::EventSchemas::Registry",
    "AWS::EventSchemas::Schema",
    "AWS::GameLift::GameSessionQueue",
    "AWS::GameLift::MatchmakingConfiguration",
    "AWS::GameLift::MatchmakingRuleSet",
    "AWS::Grafana::Workspace",
    "AWS::Greengrass::ConnectorDefinition",
    "AWS::Greengrass::CoreDefinition",
    "AWS::Greengrass::DeviceDefinition",
    "AWS::Greengrass::FunctionDefinition",
    "AWS::Greengrass::Group",
    "AWS::Greengrass::LoggerDefinition",
    "AWS::Greengrass::ResourceDefinition",
    "AWS::Greengrass::SubscriptionDefinition",
    "AWS::ImageBuilder::Component",
    "AWS::ImageBuilder::ContainerRecipe",
    "AWS::ImageBuilder::DistributionConfiguration",
    "AWS::ImageBuilder::ImagePipeline",
    "AWS::ImageBuilder::ImageRecipe",
    "AWS::ImageBuilder::InfrastructureConfiguration",
    "AWS::Neptune::DBCluster",
    "AWS::RDS::DBInstance",
    "AWS::RDS::DBParameterGroup",
    "AWS::RoboMaker::RobotApplication",
    "AWS::RoboMaker::SimulationApplication",
    "AWS::Route53Resolver::ResolverRule",
    "AWS::Route53Resolver::ResolverRuleAssociation",
    "AWS::S3::AccessPoint",
    "AWS::SageMaker::DataQualityJobDefinition",
    "AWS::SageMaker::ModelBiasJobDefinition",
    "AWS::SageMaker::ModelExplainabilityJobDefinition",
    "AWS::SageMaker::ModelQualityJobDefinition",
    "AWS::SageMaker::MonitoringSchedule",
    "AWS::SNS::Topic",
    "AWS::SQS::Queue",
    "AWS::SSM::Parameter",
    "AWS::StepFunctions::Activity",
];

/// Additional GetAtt attributes beyond readOnlyProperties for specific types.
fn get_exceptions(resource_type: &str) -> Option<&'static [&'static str]> {
    match resource_type {
        "AWS::AppMesh::GatewayRoute" => {
            Some(&["GatewayRouteName", "MeshName", "MeshOwner", "VirtualGatewayName"])
        }
        "AWS::AppMesh::Mesh" => Some(&["MeshName"]),
        "AWS::AppMesh::Route" => {
            Some(&["MeshName", "MeshOwner", "RouteName", "VirtualRouterName"])
        }
        "AWS::AppMesh::VirtualGateway" => {
            Some(&["MeshName", "MeshOwner", "VirtualGatewayName"])
        }
        "AWS::AppMesh::VirtualNode" => Some(&["MeshName", "MeshOwner", "VirtualNodeName"]),
        "AWS::AppMesh::VirtualRouter" => Some(&["MeshName", "MeshOwner", "VirtualRouterName"]),
        "AWS::AppMesh::VirtualService" => {
            Some(&["MeshName", "MeshOwner", "VirtualServiceName"])
        }
        "AWS::AppSync::DataSource" => Some(&["Name"]),
        "AWS::Cloud9::EnvironmentEC2" => Some(&["Name"]),
        "AWS::CloudWatch::InsightRule" => Some(&["RuleName"]),
        "AWS::DocDB::DBCluster" => Some(&["Port"]),
        "AWS::Greengrass::ConnectorDefinition" => Some(&["Name"]),
        "AWS::Greengrass::CoreDefinition" => Some(&["Name"]),
        "AWS::Greengrass::DeviceDefinition" => Some(&["Name"]),
        "AWS::Greengrass::FunctionDefinition" => Some(&["Name"]),
        "AWS::Greengrass::Group" => Some(&["Name", "RoleArn"]),
        "AWS::Greengrass::LoggerDefinition" => Some(&["Name"]),
        "AWS::Greengrass::ResourceDefinition" => Some(&["Name"]),
        "AWS::Greengrass::SubscriptionDefinition" => Some(&["Name"]),
        "AWS::IoT1Click::Device" => Some(&["Enabled"]),
        "AWS::IoT1Click::Placement" => Some(&["PlacementName", "ProjectName"]),
        "AWS::IoT1Click::Project" => Some(&["ProjectName"]),
        "AWS::Kinesis::StreamConsumer" => Some(&["ConsumerName", "StreamARN"]),
        "AWS::ManagedBlockchain::Member" => Some(&["NetworkId"]),
        "AWS::MediaConvert::JobTemplate" => Some(&["Name"]),
        "AWS::MediaConvert::Preset" => Some(&["Name"]),
        "AWS::MediaConvert::Queue" => Some(&["Name"]),
        "AWS::MediaLive::Input" => Some(&["Destinations", "Sources"]),
        "AWS::OpsWorks::Instance" => Some(&["AvailabilityZone"]),
        "AWS::OpsWorks::UserProfile" => Some(&["SshUsername"]),
        "AWS::Route53Resolver::ResolverEndpoint" => Some(&["Direction", "Name"]),
        "AWS::SageMaker::CodeRepository" => Some(&["CodeRepositoryName"]),
        "AWS::SageMaker::Endpoint" => Some(&["EndpointName"]),
        "AWS::SageMaker::EndpointConfig" => Some(&["EndpointConfigName"]),
        "AWS::SageMaker::Model" => Some(&["ModelName"]),
        "AWS::SageMaker::NotebookInstance" => Some(&["NotebookInstanceName"]),
        "AWS::SageMaker::NotebookInstanceLifecycleConfig" => {
            Some(&["NotebookInstanceLifecycleConfigName"])
        }
        "AWS::SageMaker::Workteam" => Some(&["WorkteamName"]),
        "AWS::ServiceDiscovery::Service" => Some(&["Name"]),
        "AWS::Transfer::User" => Some(&["ServerId", "UserName"]),
        _ => None,
    }
}

/// Returns true if the resource type accepts any GetAtt attribute.
fn is_wildcard_type(resource_type: &str) -> bool {
    resource_type.starts_with("Custom::")
        || resource_type.starts_with("AWS::Serverless::")
        || resource_type == "AWS::CloudFormation::CustomResource"
        || resource_type.ends_with("::MODULE")
        || resource_type.ends_with("::Module")
}

/// Convert a JSON pointer like `/properties/Foo/Bar` to a GetAtt attribute `Foo.Bar`.
fn pointer_to_attr(pointer: &str) -> Option<String> {
    let stripped = pointer.strip_prefix("/properties/")?;
    Some(stripped.replace('/', "."))
}

/// Recursively collect all property names from a schema object for
/// `ALL_PROPERTY_TYPES` resources. Traverses nested objects and produces
/// dotted paths (e.g. `Foo.Bar`).
fn collect_all_properties(
    obj: &serde_json::Value,
    schema_root: &serde_json::Value,
    prefix: &str,
    out: &mut Vec<String>,
) {
    let types = match obj.get("type") {
        Some(serde_json::Value::String(s)) => vec![s.as_str()],
        Some(serde_json::Value::Array(arr)) => arr.iter().filter_map(|v| v.as_str()).collect(),
        _ => {
            // Check for $ref
            if let Some(serde_json::Value::String(ref_path)) = obj.get("$ref") {
                if let Some(resolved) = resolve_ref(ref_path, schema_root) {
                    collect_all_properties(resolved, schema_root, prefix, out);
                }
            } else {
                // No type info — treat as leaf
                if !prefix.is_empty() {
                    out.push(prefix.to_string());
                }
            }
            return;
        }
    };

    if types.contains(&"object") {
        if let Some(serde_json::Value::Object(props)) = obj.get("properties") {
            for (name, value) in props {
                let path = if prefix.is_empty() {
                    name.clone()
                } else {
                    format!("{}.{}", prefix, name)
                };
                collect_all_properties(value, schema_root, &path, out);
            }
        }
    } else if types.contains(&"array") {
        // GetAtt doesn't support going into arrays of objects/arrays
        if let Some(items) = obj.get("items") {
            let item_type = items.get("type").and_then(|t| t.as_str());
            if item_type == Some("object") || item_type == Some("array") {
                return;
            }
        }
        if !prefix.is_empty() {
            out.push(prefix.to_string());
        }
    } else if !prefix.is_empty() {
        out.push(prefix.to_string());
    }
}

/// Resolve a `$ref` like `#/definitions/Foo` within the schema root.
fn resolve_ref<'a>(ref_path: &str, schema_root: &'a serde_json::Value) -> Option<&'a serde_json::Value> {
    let path = ref_path.strip_prefix("#/")?;
    let mut current = schema_root;
    for segment in path.split('/') {
        current = current.get(segment)?;
    }
    Some(current)
}

/// Get valid GetAtt attributes for a resource type given its schema.
///
/// Returns:
/// - `vec!["*"]` for wildcard types (Custom::*, AWS::Serverless::*, etc.)
/// - All property names for types in `ALL_PROPERTY_TYPES`
/// - Attributes from `readOnlyProperties` + exceptions for all other types
/// - `Outputs.*` for AWS::CloudFormation::Stack
pub fn get_valid_attributes(schema: &serde_json::Value, resource_type: &str) -> Vec<String> {
    if is_wildcard_type(resource_type) {
        return vec!["*".to_string()];
    }

    // AWS::CloudFormation::Stack supports Outputs.*
    if resource_type == "AWS::CloudFormation::Stack" {
        return vec!["Outputs.*".to_string()];
    }

    // AWS::ServiceCatalog::CloudFormationProvisionedProduct has special Outputs handling
    if resource_type == "AWS::ServiceCatalog::CloudFormationProvisionedProduct" {
        let mut attrs = Vec::new();
        if let Some(serde_json::Value::Array(ro)) = schema.get("readOnlyProperties") {
            for item in ro {
                if let Some(s) = item.as_str() {
                    if s == "/properties/Outputs" {
                        attrs.push("Outputs.*".to_string());
                    } else if let Some(attr) = pointer_to_attr(s) {
                        attrs.push(attr);
                    }
                }
            }
        }
        return attrs;
    }

    // Types that expose ALL properties as GetAtt attributes
    if ALL_PROPERTY_TYPES.contains(&resource_type) {
        let mut attrs = Vec::new();
        if let Some(serde_json::Value::Object(props)) = schema.get("properties") {
            for (name, value) in props {
                collect_all_properties(value, schema, name, &mut attrs);
            }
        }
        return attrs;
    }

    // Standard: readOnlyProperties + exceptions
    let mut attrs = Vec::new();

    if let Some(exceptions) = get_exceptions(resource_type) {
        for attr in exceptions {
            attrs.push(attr.to_string());
        }
    }

    if let Some(serde_json::Value::Array(ro)) = schema.get("readOnlyProperties") {
        for item in ro {
            if let Some(s) = item.as_str() {
                if let Some(attr) = pointer_to_attr(s) {
                    if !attrs.contains(&attr) {
                        attrs.push(attr);
                    }
                }
            }
        }
    }

    attrs
}

/// Check if an attribute matches the valid attributes list.
/// Handles wildcard patterns like `Outputs.*` and `*`.
pub fn is_valid_attribute(attribute: &str, valid_attrs: &[String]) -> bool {
    for valid in valid_attrs {
        if valid == "*" {
            return true;
        }
        if valid == attribute {
            return true;
        }
        // Handle Outputs.* pattern
        if valid.ends_with(".*") {
            let prefix = &valid[..valid.len() - 2];
            if attribute.starts_with(prefix) && attribute.len() > prefix.len() {
                let rest = &attribute[prefix.len()..];
                if rest.starts_with('.') {
                    return true;
                }
            }
        }
    }
    false
}

/// Check if a resource type exposes all properties as GetAtt attributes.
pub fn is_all_property_type(resource_type: &str) -> bool {
    ALL_PROPERTY_TYPES.contains(&resource_type)
}

/// Get the JSON Schema type(s) of a GetAtt attribute from the resource schema.
/// Returns None if the attribute type cannot be determined.
pub fn get_attribute_type(schema: &serde_json::Value, attribute: &str) -> Option<Vec<String>> {
    // Navigate to the property definition using dot-separated path
    let parts: Vec<&str> = attribute.split('.').collect();
    let mut current = schema.get("properties")?;
    for (i, part) in parts.iter().enumerate() {
        current = current.get(part)?;
        // For nested objects, descend into properties
        if i < parts.len() - 1 {
            current = current.get("properties")?;
        }
    }
    // Extract type
    match current.get("type") {
        Some(serde_json::Value::String(t)) => Some(vec![t.clone()]),
        Some(serde_json::Value::Array(arr)) => {
            Some(arr.iter().filter_map(|v| v.as_str().map(String::from)).collect())
        }
        _ => None,
    }
}

/// Get the format of a GetAtt attribute from the resource schema (after patching).
/// Returns None if the attribute has no format.
pub fn get_attribute_format(schema: &serde_json::Value, attribute: &str) -> Option<String> {
    let parts: Vec<&str> = attribute.split('.').collect();
    let mut current = schema.get("properties")?;
    for (i, part) in parts.iter().enumerate() {
        current = current.get(part)?;
        if i < parts.len() - 1 {
            current = current.get("properties")?;
        }
    }
    current.get("format").and_then(|v| v.as_str()).map(String::from)
}

/// Get the format(s) of a Ref return value for a resource type.
/// Uses the primaryIdentifier property's format from the schema.
/// Returns formats from direct `format` field or from `anyOf` entries.
pub fn get_ref_formats(schema: &serde_json::Value) -> Vec<String> {
    let pi = match schema.get("primaryIdentifier").and_then(|v| v.as_array()) {
        Some(arr) => arr,
        None => return vec![],
    };
    let first = match pi.first().and_then(|v| v.as_str()) {
        Some(s) => s,
        None => return vec![],
    };
    let prop_name = match first.strip_prefix("/properties/") {
        Some(s) => s,
        None => return vec![],
    };
    let parts: Vec<&str> = prop_name.split('/').collect();
    let mut current = match schema.get("properties") {
        Some(v) => v,
        None => return vec![],
    };
    for (i, part) in parts.iter().enumerate() {
        current = match current.get(part) {
            Some(v) => v,
            None => return vec![],
        };
        if i < parts.len() - 1 {
            current = match current.get("properties") {
                Some(v) => v,
                None => return vec![],
            };
        }
    }
    // Check direct format
    if let Some(fmt) = current.get("format").and_then(|v| v.as_str()) {
        return vec![fmt.to_string()];
    }
    // Check anyOf for formats
    if let Some(any_of) = current.get("anyOf").and_then(|v| v.as_array()) {
        return any_of
            .iter()
            .filter_map(|item| item.get("format").and_then(|v| v.as_str()).map(String::from))
            .collect();
    }
    vec![]
}

/// Navigate a resource schema to find the property schema at a given path.
/// Path segments are property names; numeric segments (array indices) are
/// skipped by descending into `items`. Resolves `$ref` pointers.
pub fn get_property_schema<'a>(
    schema: &'a serde_json::Value,
    property_path: &[&str],
) -> Option<&'a serde_json::Value> {
    let mut current = schema;
    for &segment in property_path {
        // Skip numeric array indices by descending into items
        if segment.chars().all(|c| c.is_ascii_digit()) {
            current = resolve_schema_ref(current.get("items")?, schema)?;
            continue;
        }
        // Try properties first
        if let Some(prop) = current.get("properties").and_then(|p| p.get(segment)) {
            current = resolve_schema_ref(prop, schema)?;
        } else if let Some(items) = current.get("items") {
            // If current is an array schema, descend into items then properties
            let resolved_items = resolve_schema_ref(items, schema)?;
            current = resolve_schema_ref(
                resolved_items.get("properties").and_then(|p| p.get(segment))?,
                schema,
            )?;
        } else {
            return None;
        }
    }
    Some(current)
}

/// Resolve a `$ref` in a schema value, returning the referenced schema.
/// If no `$ref`, returns the value itself.
fn resolve_schema_ref<'a>(
    value: &'a serde_json::Value,
    root: &'a serde_json::Value,
) -> Option<&'a serde_json::Value> {
    if let Some(ref_path) = value.get("$ref").and_then(|v| v.as_str()) {
        resolve_ref(ref_path, root)
    } else {
        Some(value)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn test_wildcard_custom_resource() {
        let schema = json!({});
        assert_eq!(get_valid_attributes(&schema, "Custom::MyThing"), vec!["*"]);
    }

    #[test]
    fn test_wildcard_serverless() {
        let schema = json!({});
        assert_eq!(
            get_valid_attributes(&schema, "AWS::Serverless::Function"),
            vec!["*"]
        );
    }

    #[test]
    fn test_wildcard_custom_resource_type() {
        let schema = json!({});
        assert_eq!(
            get_valid_attributes(&schema, "AWS::CloudFormation::CustomResource"),
            vec!["*"]
        );
    }

    #[test]
    fn test_wildcard_module() {
        let schema = json!({});
        assert_eq!(
            get_valid_attributes(&schema, "MyOrg::MyService::MyResource::MODULE"),
            vec!["*"]
        );
    }

    #[test]
    fn test_cloudformation_stack() {
        let schema = json!({});
        assert_eq!(
            get_valid_attributes(&schema, "AWS::CloudFormation::Stack"),
            vec!["Outputs.*"]
        );
    }

    #[test]
    fn test_readonly_properties() {
        let schema = json!({
            "readOnlyProperties": [
                "/properties/Arn",
                "/properties/DomainName",
                "/properties/WebsiteURL"
            ]
        });
        let attrs = get_valid_attributes(&schema, "AWS::S3::Bucket");
        assert!(attrs.contains(&"Arn".to_string()));
        assert!(attrs.contains(&"DomainName".to_string()));
        assert!(attrs.contains(&"WebsiteURL".to_string()));
        assert_eq!(attrs.len(), 3);
    }

    #[test]
    fn test_nested_readonly_properties() {
        let schema = json!({
            "readOnlyProperties": [
                "/properties/MetadataTableConfiguration/S3TablesDestination/TableArn"
            ]
        });
        let attrs = get_valid_attributes(&schema, "AWS::S3::TableBucket");
        assert!(attrs.contains(&"MetadataTableConfiguration.S3TablesDestination.TableArn".to_string()));
    }

    #[test]
    fn test_all_property_types() {
        let schema = json!({
            "properties": {
                "Arn": {"type": "string"},
                "QueueName": {"type": "string"},
                "QueueUrl": {"type": "string"}
            }
        });
        let attrs = get_valid_attributes(&schema, "AWS::SQS::Queue");
        assert!(attrs.contains(&"Arn".to_string()));
        assert!(attrs.contains(&"QueueName".to_string()));
        assert!(attrs.contains(&"QueueUrl".to_string()));
    }

    #[test]
    fn test_all_property_types_nested_object() {
        let schema = json!({
            "properties": {
                "Arn": {"type": "string"},
                "Config": {
                    "type": "object",
                    "properties": {
                        "SubProp": {"type": "string"}
                    }
                }
            }
        });
        let attrs = get_valid_attributes(&schema, "AWS::EC2::Instance");
        assert!(attrs.contains(&"Arn".to_string()));
        assert!(attrs.contains(&"Config.SubProp".to_string()));
    }

    #[test]
    fn test_exceptions_added() {
        let schema = json!({
            "readOnlyProperties": ["/properties/Arn"]
        });
        let attrs = get_valid_attributes(&schema, "AWS::AppMesh::Mesh");
        assert!(attrs.contains(&"MeshName".to_string()));
        assert!(attrs.contains(&"Arn".to_string()));
    }

    #[test]
    fn test_is_valid_attribute_exact() {
        let valid = vec!["Arn".to_string(), "DomainName".to_string()];
        assert!(is_valid_attribute("Arn", &valid));
        assert!(!is_valid_attribute("Missing", &valid));
    }

    #[test]
    fn test_is_valid_attribute_wildcard() {
        let valid = vec!["*".to_string()];
        assert!(is_valid_attribute("Anything", &valid));
    }

    #[test]
    fn test_is_valid_attribute_outputs_wildcard() {
        let valid = vec!["Outputs.*".to_string()];
        assert!(is_valid_attribute("Outputs.MyOutput", &valid));
        assert!(!is_valid_attribute("Arn", &valid));
        assert!(!is_valid_attribute("Outputs", &valid));
    }

    #[test]
    fn test_empty_schema_no_readonly() {
        let schema = json!({});
        let attrs = get_valid_attributes(&schema, "AWS::Lambda::Function");
        assert!(attrs.is_empty());
    }

    #[test]
    fn test_pointer_to_attr() {
        assert_eq!(pointer_to_attr("/properties/Arn"), Some("Arn".to_string()));
        assert_eq!(
            pointer_to_attr("/properties/Foo/Bar"),
            Some("Foo.Bar".to_string())
        );
        assert_eq!(pointer_to_attr("/invalid"), None);
    }

    #[test]
    fn test_all_property_types_with_ref() {
        let schema = json!({
            "definitions": {
                "Tag": {
                    "type": "string"
                }
            },
            "properties": {
                "Name": {"$ref": "#/definitions/Tag"}
            }
        });
        let attrs = get_valid_attributes(&schema, "AWS::SNS::Topic");
        assert!(attrs.contains(&"Name".to_string()));
    }

    #[test]
    fn test_all_property_types_array_of_strings() {
        let schema = json!({
            "properties": {
                "Tags": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            }
        });
        let attrs = get_valid_attributes(&schema, "AWS::EC2::SecurityGroup");
        assert!(attrs.contains(&"Tags".to_string()));
    }

    #[test]
    fn test_all_property_types_array_of_objects_excluded() {
        let schema = json!({
            "properties": {
                "Items": {
                    "type": "array",
                    "items": {"type": "object"}
                },
                "Name": {"type": "string"}
            }
        });
        let attrs = get_valid_attributes(&schema, "AWS::EC2::SecurityGroup");
        assert!(!attrs.contains(&"Items".to_string()));
        assert!(attrs.contains(&"Name".to_string()));
    }

    #[test]
    fn test_service_catalog_provisioned_product() {
        let schema = json!({
            "readOnlyProperties": [
                "/properties/Outputs",
                "/properties/RecordId"
            ]
        });
        let attrs = get_valid_attributes(
            &schema,
            "AWS::ServiceCatalog::CloudFormationProvisionedProduct",
        );
        assert!(attrs.contains(&"Outputs.*".to_string()));
        assert!(attrs.contains(&"RecordId".to_string()));
    }

    #[test]
    fn test_get_attribute_format() {
        let schema = json!({
            "properties": {
                "GroupId": {"type": "string", "format": "AWS::EC2::SecurityGroup.Id"},
                "GroupName": {"type": "string", "format": "AWS::EC2::SecurityGroup.Name"},
                "Arn": {"type": "string"}
            }
        });
        assert_eq!(
            get_attribute_format(&schema, "GroupId"),
            Some("AWS::EC2::SecurityGroup.Id".to_string())
        );
        assert_eq!(
            get_attribute_format(&schema, "GroupName"),
            Some("AWS::EC2::SecurityGroup.Name".to_string())
        );
        assert_eq!(get_attribute_format(&schema, "Arn"), None);
    }

    #[test]
    fn test_get_ref_formats_direct() {
        let schema = json!({
            "primaryIdentifier": ["/properties/VpcId"],
            "properties": {
                "VpcId": {"type": "string", "format": "AWS::EC2::VPC.Id"}
            }
        });
        assert_eq!(get_ref_formats(&schema), vec!["AWS::EC2::VPC.Id"]);
    }

    #[test]
    fn test_get_ref_formats_anyof() {
        let schema = json!({
            "primaryIdentifier": ["/properties/Id"],
            "properties": {
                "Id": {
                    "type": "string",
                    "anyOf": [
                        {"format": "AWS::EC2::SecurityGroup.Id"},
                        {"format": "AWS::EC2::SecurityGroup.Name"}
                    ]
                }
            }
        });
        let formats = get_ref_formats(&schema);
        assert_eq!(formats.len(), 2);
        assert!(formats.contains(&"AWS::EC2::SecurityGroup.Id".to_string()));
        assert!(formats.contains(&"AWS::EC2::SecurityGroup.Name".to_string()));
    }

    #[test]
    fn test_get_ref_formats_no_format() {
        let schema = json!({
            "primaryIdentifier": ["/properties/RoleName"],
            "properties": {
                "RoleName": {"type": "string"}
            }
        });
        assert!(get_ref_formats(&schema).is_empty());
    }

    #[test]
    fn test_get_property_schema_simple() {
        let schema = json!({
            "properties": {
                "Value": {"type": "string"}
            }
        });
        let result = get_property_schema(&schema, &["Value"]);
        assert!(result.is_some());
        assert_eq!(result.unwrap().get("type").unwrap(), "string");
    }

    #[test]
    fn test_get_property_schema_nested_with_ref() {
        let schema = json!({
            "definitions": {
                "NetworkInterface": {
                    "properties": {
                        "GroupSet": {
                            "type": "array",
                            "items": {"type": "string", "format": "AWS::EC2::SecurityGroup.Id"}
                        }
                    }
                }
            },
            "properties": {
                "NetworkInterfaces": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/NetworkInterface"}
                }
            }
        });
        // Navigate: NetworkInterfaces/0/GroupSet/0
        let result = get_property_schema(&schema, &["NetworkInterfaces", "0", "GroupSet", "0"]);
        assert!(result.is_some());
        assert_eq!(
            result.unwrap().get("format").unwrap(),
            "AWS::EC2::SecurityGroup.Id"
        );
    }

    #[test]
    fn test_get_property_schema_missing() {
        let schema = json!({
            "properties": {
                "Name": {"type": "string"}
            }
        });
        assert!(get_property_schema(&schema, &["Missing"]).is_none());
    }
}
