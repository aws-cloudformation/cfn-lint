use super::*;

impl Engine {
    /// Validate that no read-only properties are set in resource Properties.
    ///
    #[cfg(test)]
    pub(crate) fn validate_readonly_properties(
        &mut self,
        template: &Template,
        root: &AstNode,
        region: &str,
    ) -> Vec<ValidationError> {
        let schema_provider = match self.schema_provider.as_ref() {
            Some(p) => p,
            None => return vec![],
        };

        let mut issues = Vec::new();

        let resources: Vec<(String, String, Option<AstNode>)> = template
            .resources
            .iter()
            .map(|(name, res)| (name.clone(), res.resource_type.clone(), res.properties.clone()))
            .collect();

        for (name, resource_type, properties) in &resources {
            let props_node = match properties {
                Some(p) => p,
                None => continue,
            };

            let schema = match schema_provider.get_resource_schema(resource_type, region) {
                Some(s) => s.raw.clone(),
                None => continue,
            };

            let read_only = match schema.get("readOnlyProperties").and_then(|v| v.as_array()) {
                Some(arr) => arr,
                None => continue,
            };

            let props_obj = match props_node.as_object() {
                Some(o) => o,
                None => continue,
            };

            for ro_val in read_only {
                let pointer = match ro_val.as_str() {
                    Some(s) => s,
                    None => continue,
                };
                // readOnlyProperties are like "/properties/Arn"
                let prop_name = match pointer.strip_prefix("/properties/") {
                    Some(p) => p,
                    None => continue,
                };
                // Only check top-level properties (no nested paths with /)
                if prop_name.contains('/') {
                    continue;
                }
                if props_obj.contains_key(prop_name) {
                    let pos = root
                        .get("Resources")
                        .and_then(|r| r.get(name))
                        .and_then(|r| r.get("Properties"))
                        .and_then(|p| p.get(prop_name))
                        .map(|n| n.span().clone())
                        .unwrap_or_default();
                    issues.push(ValidationError {
                        rule_id: Some("E3040".to_string()),
                        message: format!(
                            "Read only property '{}' is not allowed on resource type '{}'",
                            prop_name, resource_type
                        ),
                        path: vec![
                            "Resources".to_string(),
                            name.clone(),
                            "Properties".to_string(),
                            prop_name.to_string(),
                        ],
                        span: pos,
                        keyword: String::new(),
                        unknown: false,
                        resolved_from_ref: false,
                        context: vec![],
                        schema_id: None,
                    });
                }
            }
        }

        issues
    }
}
