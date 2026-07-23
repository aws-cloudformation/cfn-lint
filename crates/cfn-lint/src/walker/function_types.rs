use std::sync::LazyLock;

use regex::Regex;

use crate::ast::{AstNode, FunctionNode};
use crate::getatts;
use crate::jsonschema::ValidationError;
use crate::template::Template;

use super::TemplateWalker;

static RE_FN_SUB_VARS: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"\$\{([^!][^}]*)\}").unwrap());

impl TemplateWalker {
    /// Validate that output values using Fn::GetAtt resolve to string types.
    /// Checks GetAtt calls in Outputs/*/Value, including inside Fn::Sub and Fn::Join.
    pub(super) fn validate_output_getatt_types(
        &self,
        template: &Template,
        root: &AstNode,
        region: &str,
    ) -> Vec<ValidationError> {
        let outputs = match root.get("Outputs").and_then(|n| n.as_object()) {
            Some(obj) => obj,
            None => return vec![],
        };

        let mut issues = Vec::new();

        for (name, node) in outputs.iter() {
            let value = match node.get("Value") {
                Some(v) => v,
                None => continue,
            };
            self.check_output_value_type(
                template,
                value,
                name,
                &["Outputs".into(), name.to_string(), "Value".into()],
                region,
                &mut issues,
            );
        }

        issues
    }

    fn check_output_value_type(
        &self,
        template: &Template,
        node: &AstNode,
        _output_name: &str,
        path: &[String],
        region: &str,
        issues: &mut Vec<ValidationError>,
    ) {
        if let AstNode::Function(func) = node {
            match func.name.as_str() {
                "Fn::GetAtt" => {
                    if let Some((resource_name, attribute)) =
                        crate::rules::e3015::parse_getatt_args(func)
                    {
                        // First check if the attribute is valid
                        if let Some(resource) = template.resources.get(&resource_name) {
                            let valid_attrs =
                                self.get_output_getatt_valid_attrs(&resource.resource_type, region);
                            if !valid_attrs.is_empty()
                                && !getatts::is_valid_attribute(&attribute, &valid_attrs)
                            {
                                let mut p = path.to_vec();
                                p.push("Fn::GetAtt".into());
                                p.push("1".into());
                                issues.push(ValidationError::new(
                                    "E6101",
                                    format!(
                                        "'{}' is not one of {:?} in ['{}']",
                                        attribute, valid_attrs, region
                                    ),
                                    p,
                                    func.span,
                                ));
                                return;
                            }
                        }
                        // Then check type
                        if let Some(attr_types) =
                            self.get_getatt_type(template, &resource_name, &attribute, region)
                        {
                            if !attr_types.iter().any(|t| t == "string") {
                                let mut p = path.to_vec();
                                p.push("Fn::GetAtt".into());
                                issues.push(ValidationError::new(
                                    "E6101",
                                    format!(
                                        "{{'Fn::GetAtt': ['{}', '{}']}} is not of type 'string'",
                                        resource_name, attribute
                                    ),
                                    p,
                                    func.span,
                                ));
                            }
                        }
                    }
                }
                "Fn::Sub" => {
                    // Check Fn::Sub with context map containing GetAtt
                    if let AstNode::Array(arr) = func.args.as_ref() {
                        if arr.elements.len() == 2 {
                            // Check context map values
                            if let AstNode::Object(ctx_map) = &arr.elements[1] {
                                for (key, val) in ctx_map.iter() {
                                    if let AstNode::Function(inner_func) = val {
                                        if inner_func.name == "Fn::GetAtt" {
                                            if let Some((rn, attr)) =
                                                crate::rules::e3015::parse_getatt_args(inner_func)
                                            {
                                                if let Some(attr_types) = self
                                                    .get_getatt_type(template, &rn, &attr, region)
                                                {
                                                    if !attr_types.iter().any(|t| t == "string") {
                                                        let mut p = path.to_vec();
                                                        p.extend([
                                                            "Fn::Sub".into(),
                                                            "1".into(),
                                                            key.to_string(),
                                                            "Fn::GetAtt".into(),
                                                        ]);
                                                        issues.push(ValidationError::new(
                                                        "E6101",
                                                        format!("{{'Fn::GetAtt': ['{}', '{}']}} is not of type 'string'", rn, attr),
                                                        p,
                                                        inner_func.span,
                                                    ));
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                    // Check Fn::Sub with ${Resource.Attribute} pattern
                    let template_str = match func.args.as_ref() {
                        AstNode::String(s) => Some(&s.value),
                        AstNode::Array(arr) if !arr.elements.is_empty() => {
                            if let AstNode::String(s) = &arr.elements[0] {
                                Some(&s.value)
                            } else {
                                None
                            }
                        }
                        _ => None,
                    };
                    if let Some(tmpl_str) = template_str {
                        for cap in RE_FN_SUB_VARS.captures_iter(tmpl_str) {
                            let var = &cap[1];
                            if let Some(dot_pos) = var.find('.') {
                                let rn = &var[..dot_pos];
                                let attr = &var[dot_pos + 1..];
                                // Check if it's a context map variable (skip those)
                                if let AstNode::Array(arr) = func.args.as_ref() {
                                    if arr.elements.len() == 2 {
                                        if let AstNode::Object(ctx_map) = &arr.elements[1] {
                                            if ctx_map.contains_key(var) {
                                                continue;
                                            }
                                        }
                                    }
                                }
                                if let Some(attr_types) =
                                    self.get_getatt_type(template, rn, attr, region)
                                {
                                    if !attr_types.iter().any(|t| t == "string") {
                                        let mut p = path.to_vec();
                                        p.push("Fn::Sub".into());
                                        issues.push(ValidationError::new(
                                            "E6101",
                                            format!("'{}' is not of type 'string'", var),
                                            p,
                                            func.span,
                                        ));
                                    }
                                } else if let Some(resource) = template.resources.get(rn) {
                                    // Check attribute validity even when type can't be determined
                                    let valid_attrs = self.get_output_getatt_valid_attrs(
                                        &resource.resource_type,
                                        region,
                                    );
                                    if !valid_attrs.is_empty()
                                        && !getatts::is_valid_attribute(attr, &valid_attrs)
                                    {
                                        let mut p = path.to_vec();
                                        p.push("Fn::Sub".into());
                                        issues.push(ValidationError::new(
                                            "E6101",
                                            format!(
                                                "'{}' is not one of {:?} in ['{}']",
                                                attr, valid_attrs, region
                                            ),
                                            p,
                                            func.span,
                                        ));
                                    }
                                }
                            }
                        }
                    }
                }
                "Fn::Join" => {
                    // Check elements of Fn::Join for non-string GetAtts
                    if let AstNode::Array(arr) = func.args.as_ref() {
                        if arr.elements.len() == 2 {
                            if let AstNode::Array(items) = &arr.elements[1] {
                                for (i, item) in items.elements.iter().enumerate() {
                                    if let AstNode::Function(inner_func) = item {
                                        if inner_func.name == "Fn::GetAtt" {
                                            if let Some((rn, attr)) =
                                                crate::rules::e3015::parse_getatt_args(inner_func)
                                            {
                                                if let Some(attr_types) = self
                                                    .get_getatt_type(template, &rn, &attr, region)
                                                {
                                                    if !attr_types.iter().any(|t| t == "string") {
                                                        let mut p = path.to_vec();
                                                        p.extend([
                                                            "Fn::Join".into(),
                                                            "1".into(),
                                                            i.to_string(),
                                                            "Fn::GetAtt".into(),
                                                        ]);
                                                        issues.push(ValidationError::new(
                                                        "E6101",
                                                        format!("{{'Fn::GetAtt': ['{}', '{}']}} is not of type 'string'", rn, attr),
                                                        p,
                                                        inner_func.span,
                                                    ));
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
                _ => {}
            }
        }
    }

    fn get_getatt_type(
        &self,
        template: &Template,
        resource_name: &str,
        attribute: &str,
        region: &str,
    ) -> Option<Vec<String>> {
        let resource = template.resources.get(resource_name)?;
        // Only check types for resources in ALL_PROPERTY_TYPES where
        // schema property types reliably reflect GetAtt return types
        if !getatts::is_all_property_type(&resource.resource_type) {
            return None;
        }
        let schema_provider = self.schema_provider.as_ref()?;
        let schema = schema_provider.get_resource_schema(&resource.resource_type, region)?;
        getatts::get_attribute_type(&schema.raw, attribute)
    }

    fn get_output_getatt_valid_attrs(&self, resource_type: &str, region: &str) -> Vec<String> {
        let schema_provider = match self.schema_provider.as_ref() {
            Some(p) => p,
            None => return vec![],
        };
        match schema_provider.get_resource_schema(resource_type, region) {
            Some(schema) => getatts::get_valid_attributes(&schema.raw, resource_type),
            None => getatts::get_valid_attributes(&serde_json::json!({}), resource_type),
        }
    }

    /// Validate GetAtt/Ref return types and formats against destination property schemas.
    ///
    /// Produces:
    /// - E1010: GetAtt type mismatch (e.g. integer attribute used where string expected)
    /// - E1040: GetAtt format mismatch (e.g. SecurityGroup.Name where SecurityGroup.Id expected)
    /// - E1041: Ref format mismatch (e.g. IAM::Role ref where VPC.Id expected)
    pub(super) fn validate_function_types(
        &self,
        template: &Template,
        root: &AstNode,
        regions: &[String],
    ) -> Vec<ValidationError> {
        let schema_provider = match self.schema_provider.as_ref() {
            Some(p) => p,
            None => return vec![],
        };

        let region = regions.first().map(|s| s.as_str()).unwrap_or("us-east-1");

        // Collect all GetAtt and Ref calls with their paths
        let mut function_calls: Vec<(FunctionNode, Vec<String>)> = Vec::new();
        crate::ast::walk(root, &[], &mut |node, path| {
            if let AstNode::Function(func) = node {
                if func.name == "Fn::GetAtt" || func.name == "Ref" {
                    function_calls.push((func.clone(), path.to_vec()));
                }
            }
            true
        });

        let mut issues = Vec::new();

        for (func, path) in &function_calls {
            // Must be inside Resources/X/Properties/... to have a destination schema
            if path.len() < 4 || path[0] != "Resources" || path[2] != "Properties" {
                continue;
            }
            let dest_resource_name = &path[1];
            let property_path_segments: Vec<&str> = path[3..].iter().map(|s| s.as_str()).collect();

            // Get destination resource type and schema
            let dest_resource = match template.resources.get(dest_resource_name.as_str()) {
                Some(r) => r,
                None => continue,
            };
            let dest_schema =
                match schema_provider.get_resource_schema(&dest_resource.resource_type, region) {
                    Some(s) => s.raw.clone(),
                    None => continue,
                };

            // Navigate to the destination property schema
            let dest_prop_schema =
                getatts::get_property_schema(&dest_schema, &property_path_segments);

            let dest_type = dest_prop_schema
                .and_then(|s| s.get("type"))
                .and_then(|v| v.as_str());
            let dest_format_from_schema = dest_prop_schema
                .and_then(|s| s.get("format"))
                .and_then(|v| v.as_str());

            // If no format from main schema, don't use extension schemas
            // because they have conditional formats (if/then) that can't be
            // properly evaluated without resource property values.
            let dest_format = dest_format_from_schema;

            // Skip format checking for Lambda EventSourceMapping properties that
            // accept multiple resource formats (FunctionName, EventSourceArn)
            if dest_resource.resource_type == "AWS::Lambda::EventSourceMapping" {
                if let Some(last) = property_path_segments.last() {
                    if *last == "FunctionName" || *last == "EventSourceArn" {
                        continue;
                    }
                }
            }

            match func.name.as_str() {
                "Fn::GetAtt" => {
                    let (resource_name, attribute) =
                        match crate::rules::e3015::parse_getatt_args(func) {
                            Some(pair) => pair,
                            None => continue,
                        };
                    let source_resource = match template.resources.get(&resource_name) {
                        Some(r) => r,
                        None => continue,
                    };
                    // Skip custom resources, stacks, modules — return types unknown
                    let src_type = &source_resource.resource_type;
                    if src_type == "AWS::CloudFormation::CustomResource"
                        || src_type.starts_with("Custom::")
                        || src_type == "AWS::CloudFormation::Stack"
                        || src_type == "AWS::ServiceCatalog::CloudFormationProvisionedProduct"
                        || src_type.ends_with("::MODULE")
                    {
                        continue;
                    }
                    let source_schema = match schema_provider
                        .get_resource_schema(&source_resource.resource_type, region)
                    {
                        Some(s) => s.raw.clone(),
                        None => continue,
                    };

                    // E1010: Type mismatch
                    if let Some(dest_t) = dest_type {
                        if let Some(source_types) =
                            getatts::get_attribute_type(&source_schema, &attribute)
                        {
                            let type_matches = source_types.iter().any(|st| {
                                st == dest_t
                                    || (dest_t == "number" && st == "integer")
                                    || (dest_t == "integer" && st == "number")
                            });
                            if !type_matches {
                                issues.push(ValidationError::new(
                                    "E1010",
                                    format!(
                                        "{{'Fn::GetAtt': ['{}', '{}']}} is not of type '{}'",
                                        resource_name, attribute, dest_t
                                    ),
                                    path.clone(),
                                    func.span,
                                ));
                                continue; // Don't also check format if type mismatches
                            }
                        }
                    }

                    // E1040: Format mismatch
                    if let Some(dest_fmt) = dest_format {
                        // Skip non-AWS formats (like ipv4-network)
                        if !dest_fmt.starts_with("AWS::") {
                            continue;
                        }
                        let source_format =
                            getatts::get_attribute_format(&source_schema, &attribute);
                        match &source_format {
                            Some(src_fmt) if src_fmt == dest_fmt => {} // Match
                            Some(src_fmt) => {
                                issues.push(ValidationError::new(
                                    "E1040",
                                    format!("{{'Fn::GetAtt': ['{}', '{}']}} with formats ['{}'] does not match destination format of '{}'", resource_name, attribute, src_fmt, dest_fmt),
                                    path.clone(),
                                    func.span,
                                ));
                            }
                            None => {
                                // Source has no format but destination expects one
                                issues.push(ValidationError::new(
                                    "E1040",
                                    format!("{{'Fn::GetAtt': ['{}', '{}']}} does not match destination format of '{}'", resource_name, attribute, dest_fmt),
                                    path.clone(),
                                    func.span,
                                ));
                            }
                        }
                    }
                }
                "Ref" => {
                    let ref_name = match func.args.as_str() {
                        Some(s) => s,
                        None => continue,
                    };
                    // Skip pseudo-parameters and parameters
                    if ref_name.starts_with("AWS::") || template.parameters.contains_key(ref_name) {
                        continue;
                    }
                    let source_resource = match template.resources.get(ref_name) {
                        Some(r) => r,
                        None => continue,
                    };

                    // E1041: Ref format mismatch
                    if let Some(dest_fmt) = dest_format {
                        if !dest_fmt.starts_with("AWS::") {
                            continue;
                        }
                        let source_schema = match schema_provider
                            .get_resource_schema(&source_resource.resource_type, region)
                        {
                            Some(s) => s.raw.clone(),
                            None => continue,
                        };
                        let source_formats = getatts::get_ref_formats(&source_schema);

                        // For AWS::EC2::SecurityGroup, the Ref format depends on
                        // whether VpcId is specified in the resource properties.
                        // With VpcId: returns SecurityGroup.Id
                        // Without VpcId: returns SecurityGroup.Name
                        let effective_formats =
                            if source_resource.resource_type == "AWS::EC2::SecurityGroup" {
                                let has_vpc_id = source_resource
                                    .properties
                                    .as_ref()
                                    .and_then(|p| p.get("VpcId"))
                                    .is_some();
                                if has_vpc_id {
                                    vec!["AWS::EC2::SecurityGroup.Id".to_string()]
                                } else {
                                    vec!["AWS::EC2::SecurityGroup.Name".to_string()]
                                }
                            } else {
                                source_formats
                            };

                        // If source has any format that matches destination, it's OK
                        if effective_formats.iter().any(|f| f == dest_fmt) {
                            continue;
                        }
                        let msg = if effective_formats.is_empty() {
                            format!(
                                "{{'Ref': '{}'}} does not match destination format of '{}'",
                                ref_name, dest_fmt
                            )
                        } else {
                            format!(
                                "{{'Ref': '{}'}} with formats {:?} does not match destination format of '{}'",
                                ref_name, effective_formats, dest_fmt
                            )
                        };
                        issues.push(ValidationError::new("E1041", msg, path.clone(), func.span));
                    }
                }
                _ => {}
            }
        }

        issues
    }
}
