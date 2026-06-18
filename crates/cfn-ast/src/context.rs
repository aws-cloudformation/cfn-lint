use std::collections::HashMap;
use std::sync::Arc;

use indexmap::IndexMap;

use crate::node::*;

#[derive(Debug, Clone)]
pub struct ParameterInfo {
    pub param_type: String,
    pub default: Option<AstNode>,
    pub allowed_values: Option<Vec<AstNode>>,
    pub description: Option<String>,
    pub span: Span,
}

#[derive(Debug, Clone)]
pub struct ResourceInfo {
    pub resource_type: String,
    pub properties: Option<AstNode>,
    pub condition: Option<String>,
    pub depends_on: Vec<String>,
    pub span: Span,
}

/// The shared core for LSP navigation and cfn-lint validation.
/// Built by indexing the AstNode tree — lenient, no errors emitted.
#[derive(Clone)]
pub struct Context {
    pub root: Arc<AstNode>,
    pub parameters: IndexMap<String, ParameterInfo>,
    pub resources: IndexMap<String, ResourceInfo>,
    pub conditions: IndexMap<String, AstNode>,
    pub mappings: IndexMap<String, AstNode>,
    pub outputs: IndexMap<String, AstNode>,

    // Evolving state for validation
    pub ref_values: HashMap<String, AstNode>,
    pub condition_state: HashMap<String, bool>,
    pub regions: Vec<String>,
}

impl Context {
    pub fn from_ast(root: Arc<AstNode>) -> Self {
        let mut ctx = Context {
            root: Arc::clone(&root),
            parameters: IndexMap::new(),
            resources: IndexMap::new(),
            conditions: IndexMap::new(),
            mappings: IndexMap::new(),
            outputs: IndexMap::new(),
            ref_values: HashMap::new(),
            condition_state: HashMap::new(),
            regions: vec!["us-east-1".to_string()],
        };
        ctx.index_section(&root);
        ctx
    }

    fn index_section(&mut self, root: &AstNode) {
        let obj = match root.as_object() {
            Some(o) => o,
            None => return,
        };

        if let Some(params) = obj.get("Parameters").and_then(|n| n.as_object()) {
            self.index_parameters(params);
        }
        if let Some(mappings) = obj.get("Mappings").and_then(|n| n.as_object()) {
            for (name, node) in mappings.iter() {
                self.mappings.insert(name.to_string(), node.clone());
            }
        }
        if let Some(conditions) = obj.get("Conditions").and_then(|n| n.as_object()) {
            for (name, node) in conditions.iter() {
                self.conditions.insert(name.to_string(), node.clone());
            }
        }
        if let Some(resources) = obj.get("Resources").and_then(|n| n.as_object()) {
            self.index_resources(resources);
        }
        if let Some(outputs) = obj.get("Outputs").and_then(|n| n.as_object()) {
            for (name, node) in outputs.iter() {
                self.outputs.insert(name.to_string(), node.clone());
            }
        }
    }

    fn index_parameters(&mut self, params: &ObjectNode) {
        for (name, node) in params.iter() {
            let obj = match node.as_object() {
                Some(o) => o,
                None => continue,
            };
            let param_type = match obj.get("Type").and_then(|n| n.as_str()) {
                Some(t) => t.to_string(),
                None => continue,
            };
            let default = obj.get("Default").cloned();
            let allowed_values = obj
                .get("AllowedValues")
                .and_then(|n| n.as_array())
                .map(|a| a.elements.clone());

            let description = obj
                .get("Description")
                .and_then(|n| n.as_str())
                .map(String::from);

            self.parameters.insert(
                name.to_string(),
                ParameterInfo {
                    param_type,
                    default,
                    allowed_values,
                    description,
                    span: node.span(),
                },
            );
        }
    }

    fn index_resources(&mut self, resources: &ObjectNode) {
        for (name, node) in resources.iter() {
            let obj = match node.as_object() {
                Some(o) => o,
                None => continue,
            };
            let resource_type = match obj.get("Type").and_then(|n| n.as_str()) {
                Some(t) => t.to_string(),
                None => continue,
            };
            let properties = obj.get("Properties").cloned();
            let condition = obj
                .get("Condition")
                .and_then(|n| n.as_str())
                .map(String::from);
            let depends_on = match obj.get("DependsOn") {
                Some(AstNode::String(s)) => vec![s.value.clone()],
                Some(AstNode::Array(a)) => a
                    .elements
                    .iter()
                    .filter_map(|e| e.as_str().map(String::from))
                    .collect(),
                _ => vec![],
            };

            self.resources.insert(
                name.to_string(),
                ResourceInfo {
                    resource_type,
                    properties,
                    condition,
                    depends_on,
                    span: node.span(),
                },
            );
        }
    }

    pub fn evolve(&self, opts: ContextOptions) -> Context {
        Context {
            root: Arc::clone(&self.root),
            parameters: self.parameters.clone(),
            resources: self.resources.clone(),
            conditions: self.conditions.clone(),
            mappings: self.mappings.clone(),
            outputs: self.outputs.clone(),
            ref_values: opts.ref_values.unwrap_or_else(|| self.ref_values.clone()),
            condition_state: opts
                .condition_state
                .unwrap_or_else(|| self.condition_state.clone()),
            regions: opts.regions.unwrap_or_else(|| self.regions.clone()),
        }
    }
}

#[derive(Default)]
pub struct ContextOptions {
    pub ref_values: Option<HashMap<String, AstNode>>,
    pub condition_state: Option<HashMap<String, bool>>,
    pub regions: Option<Vec<String>>,
}
