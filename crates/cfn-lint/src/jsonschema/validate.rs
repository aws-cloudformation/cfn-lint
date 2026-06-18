use std::sync::Arc;

use crate::ast::AstNode;

use super::{ValidationError, Validator, SKIP_KEYWORDS};

impl Validator {
    /// Top-level validate: sets root schema and returns a ValidationResult.
    pub fn validate(
        &self,
        node: &AstNode,
        schema: &serde_json::Value,
        path: &[String],
    ) -> Vec<ValidationError> {
        self.validate_schema(node, schema, path)
            .into_iter()
            .filter(|e| !e.unknown)
            .collect()
    }

    /// Internal recursive validation against a schema object.
    pub fn validate_schema(
        &self,
        node: &AstNode,
        schema: &serde_json::Value,
        path: &[String],
    ) -> Vec<ValidationError> {
        // Boolean schemas: false = always fails, true = always passes
        if let Some(b) = schema.as_bool() {
            if !b {
                return vec![ValidationError::schema_error(
                    "additionalProperties",
                    "False schema: value is not allowed",
                    path.to_vec(),
                    node.span(),
                )];
            }
            return vec![];
        }

        let schema_obj = match schema.as_object() {
            Some(obj) => obj,
            None => return vec![],
        };

        // Handle $ref: resolve and validate, then also validate sibling keywords
        if let Some(ref_val) = schema_obj.get("$ref") {
            if let Some(ref_str) = ref_val.as_str() {
                match self.resolve_ref(ref_str) {
                    Ok(resolved) => {
                        let mut errors = self.validate_schema(node, &resolved, path);
                        // Also validate sibling keywords (excluding $ref itself)
                        let siblings: serde_json::Map<String, serde_json::Value> = schema_obj
                            .iter()
                            .filter(|(k, _)| k.as_str() != "$ref")
                            .map(|(k, v)| (k.clone(), v.clone()))
                            .collect();
                        if !siblings.is_empty() {
                            errors.extend(self.validate_schema(
                                node,
                                &serde_json::Value::Object(siblings),
                                path,
                            ));
                        }
                        return errors;
                    }
                    Err(msg) => {
                        return vec![ValidationError::schema_error(
                            "$ref",
                            format!("failed to resolve $ref \"{}\": {}", ref_str, msg),
                            path.to_vec(),
                            node.span(),
                        )];
                    }
                }
            }
        }

        // Filter: route functions/dynamic refs to their keyword handlers
        let filtered = self.filter(node, schema, path);

        let mut errors = Vec::new();

        // Structural checks on object nodes: duplicate keys and non-string keys.
        // These fire on every object the validator encounters, regardless of schema.
        if let Some(obj) = node.as_object() {
            for entry in &obj.duplicate_keys() {
                errors.push(ValidationError::schema_error(
                    "E0002",
                    format!("Duplicate key '{}' found", entry.key),
                    path.to_vec(),
                    entry.key_span,
                ));
            }
            for entry in &obj.non_string_key_entries() {
                // Skip numeric keys — CloudFormation coerces them to strings
                if entry.key.parse::<f64>().is_ok() {
                    continue;
                }
                errors.push(ValidationError::schema_error(
                    "E0000",
                    format!("Non-string key found: '{}'", entry.key),
                    path.to_vec(),
                    entry.key_span,
                ));
            }
        }

        for (instance, modified_schema, evolved_ctx) in &filtered {
            let modified_obj = match modified_schema.as_object() {
                Some(obj) => obj,
                None => continue,
            };

            // If filter produced an evolved context, create a temporary validator
            let validator_for_instance: Option<Validator>;
            let v = if let Some(ctx) = evolved_ctx {
                validator_for_instance = Some(Validator {
                    validators: Arc::clone(&self.validators),
                    root_schema: self.root_schema.clone(),
                    store: self.store.clone(),
                    strict_types: self.strict_types,
                    context: Some(Arc::clone(ctx)),
                    cfn_lint_rules: self.cfn_lint_rules.clone(),
                    cfn_path: self.cfn_path.clone(),
                });
                validator_for_instance.as_ref().unwrap()
            } else {
                self
            };

            for (keyword, constraint) in modified_obj {
                if SKIP_KEYWORDS.contains(&keyword.as_str()) {
                    continue;
                }
                if let Some(validator_fn) = v.validators.get(keyword) {
                    let keyword_errors =
                        validator_fn(v, instance, constraint, &modified_schema, path);
                    errors.extend(keyword_errors);
                }
            }
        }
        errors
    }

    /// Resolve a `$ref` string against the root schema or the store.
    ///
    /// Supports:
    /// - `#/definitions/Tag` — local ref into root_schema
    /// - `policy#/definitions/Action` — cross-schema ref into store
    /// - `#` — the root schema itself
    fn resolve_ref(&self, ref_str: &str) -> Result<serde_json::Value, String> {
        let (schema_name, pointer) = match ref_str.split_once('#') {
            Some((name, ptr)) => (name, ptr),
            None => {
                // No '#' at all — treat as a store schema name with no pointer
                let schema = self
                    .store
                    .get(ref_str)
                    .ok_or_else(|| format!("schema \"{}\" not found in store", ref_str))?;
                return Ok(schema.clone());
            }
        };

        let base_schema = if schema_name.is_empty() {
            &self.root_schema
        } else {
            self.store
                .get(schema_name)
                .ok_or_else(|| format!("schema \"{}\" not found in store", schema_name))?
        };

        let path = pointer.trim_start_matches('/');
        if path.is_empty() {
            return Ok(base_schema.clone());
        }

        let mut current = base_schema;
        for segment in path.split('/') {
            let seg = segment.replace("~1", "/").replace("~0", "~");
            match current.as_object() {
                Some(obj) => match obj.get(&seg) {
                    Some(child) => current = child,
                    None => return Err(format!("segment \"{}\" not found", seg)),
                },
                None => return Err(format!("cannot traverse non-object at segment \"{}\"", seg)),
            }
        }
        let mut result = current.clone();
        // When resolving from a cross-schema source, rewrite local $refs
        // to point back to that source so nested resolution works.
        if !schema_name.is_empty() {
            rewrite_local_refs(&mut result, schema_name);
        }
        Ok(result)
    }

    /// Return a reference to the root schema used for `$ref` resolution.
    pub fn root_schema(&self) -> &serde_json::Value {
        &self.root_schema
    }
}

/// Rewrite local `$ref`s (`#/...`) to cross-schema refs (`schema_name#/...`)
/// so they resolve against the correct source schema.
fn rewrite_local_refs(value: &mut serde_json::Value, schema_name: &str) {
    match value {
        serde_json::Value::Object(map) => {
            if let Some(serde_json::Value::String(r)) = map.get_mut("$ref") {
                if r.starts_with('#') {
                    *r = format!("{}{}", schema_name, r);
                }
            }
            for v in map.values_mut() {
                rewrite_local_refs(v, schema_name);
            }
        }
        serde_json::Value::Array(arr) => {
            for v in arr {
                rewrite_local_refs(v, schema_name);
            }
        }
        _ => {}
    }
}
