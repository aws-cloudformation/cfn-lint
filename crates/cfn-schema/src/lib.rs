pub mod patch;

use std::collections::HashMap;
use std::path::PathBuf;

use indexmap::IndexMap;

/// A node in a resolved schema tree. Represents the schema at any depth.
/// Used by IDE features (completion, hover) and validation.
#[derive(Debug, Clone)]
pub struct SchemaNode {
    // Type
    pub schema_type: Vec<String>,

    // Object
    pub properties: IndexMap<String, SchemaNode>,
    pub required: Vec<String>,
    pub additional_properties: Option<AdditionalProperties>,
    pub pattern_properties: Vec<(String, SchemaNode)>,
    pub dependent_required: IndexMap<String, Vec<String>>,
    pub dependent_excluded: IndexMap<String, Vec<String>>,
    pub max_properties: Option<u64>,
    pub min_properties: Option<u64>,
    pub property_names: Option<Box<SchemaNode>>,
    pub required_xor: Option<Vec<String>>,
    pub required_or: Option<Vec<String>>,

    // Array
    pub items: Option<Box<SchemaNode>>,
    pub min_items: Option<u64>,
    pub max_items: Option<u64>,
    pub unique_items: Option<bool>,
    pub unique_keys: Option<Vec<String>>,
    pub max_unique_items: Option<u64>,
    pub prefix_items: Vec<SchemaNode>,
    pub contains: Option<Box<SchemaNode>>,

    // String
    pub pattern: Option<String>,
    pub min_length: Option<u64>,
    pub max_length: Option<u64>,
    pub format: Option<String>,

    // Numeric
    pub minimum: Option<f64>,
    pub maximum: Option<f64>,
    pub exclusive_minimum: Option<f64>,
    pub exclusive_maximum: Option<f64>,
    pub multiple_of: Option<f64>,

    // Value
    pub enum_values: Option<Vec<serde_json::Value>>,
    pub enum_case_insensitive: Option<Vec<String>>,
    pub const_value: Option<serde_json::Value>,

    // Composition
    pub all_of: Vec<SchemaNode>,
    pub any_of: Vec<SchemaNode>,
    pub one_of: Vec<SchemaNode>,
    pub not: Option<Box<SchemaNode>>,
    pub if_schema: Option<Box<SchemaNode>>,
    pub then_schema: Option<Box<SchemaNode>>,
    pub else_schema: Option<Box<SchemaNode>>,

    // IDE
    pub description: Option<String>,
    pub read_only: bool,

    // CFN extensions (opaque config blobs — not schema keywords)
    pub cfn_lint: Option<serde_json::Value>,

    // Temporary: kept until keyword rules are migrated off raw JSON
    pub raw: serde_json::Value,
}

#[derive(Debug, Clone)]
pub enum AdditionalProperties {
    Bool(bool),
    Schema(Box<SchemaNode>),
}

impl SchemaNode {
    pub fn allowed_values(&self) -> Option<Vec<String>> {
        self.enum_values.as_ref().map(|vals| {
            vals.iter().filter_map(|v| v.as_str().map(String::from)).collect()
        })
    }

    pub fn has_composition(&self) -> bool {
        !self.any_of.is_empty()
            || !self.one_of.is_empty()
            || self.if_schema.is_some()
    }
}

/// A fully loaded resource schema with pre-parsed top-level info.
#[derive(Debug, Clone)]
pub struct ResourceSchema {
    pub resource_type: String,
    pub description: Option<String>,
    pub root: SchemaNode,
    pub read_only_paths: Vec<String>,
    pub raw: serde_json::Value,
}

/// The contract for providing CloudFormation schemas.
/// Implementations own the store — they load, cache, resolve $refs, etc.
pub trait SchemaProvider: Send + Sync {
    /// Resolve a schema at a schema path.
    /// Path uses resource types, not logical IDs:
    ///   ["Resources", "AWS::S3::Bucket", "Properties", "BucketName"]
    ///   ["Resources", "AWS::AutoScaling::ASG", "UpdatePolicy"]
    ///   ["Parameters", "*", "AllowedValues"]
    fn resolve(&self, path: &[&str], region: &str) -> Option<SchemaNode>;

    /// Get the full resource schema for a type in a region.
    fn get_resource_schema(&self, resource_type: &str, region: &str) -> Option<&ResourceSchema>;

    /// All known resource types for a region (for completion).
    fn resource_types(&self, region: &str) -> Vec<String>;

    /// Group regions by schema version for a resource type.
    /// Returns (schema, regions_using_it) pairs — one per unique schema.
    fn schemas_for_regions<'a>(
        &'a self,
        resource_type: &str,
        regions: &'a [String],
    ) -> Vec<(&'a ResourceSchema, Vec<&'a str>)>;

    /// Get the raw template-level schema (top-level keys like Resources, Parameters, etc.)
    fn get_template_schema(&self) -> Option<&serde_json::Value> { None }

    /// Get a raw "other" schema by dot-path (e.g. "transforms/configuration", "parameters/configuration").
    fn get_other_schema(&self, _path: &str) -> Option<&serde_json::Value> { None }
}

/// Reads pre-patched schemas from disk. No patching at runtime.
pub struct BundledSchemaProvider {
    data_dir: PathBuf,
    /// region → (resource_type → hash)
    registry: HashMap<String, HashMap<String, String>>,
    /// SAM resource_type → hash (loaded from schemas/sam/provider.json)
    sam_registry: HashMap<String, String>,
    /// hash → loaded schema (lazy cache; Box for stable heap address)
    cache: std::sync::RwLock<HashMap<String, Box<ResourceSchema>>>,
    /// Path prefix schemas (UpdatePolicy, CreationPolicy, Parameters, etc.)
    prefix_schemas: HashMap<String, serde_json::Value>,
}

impl BundledSchemaProvider {
    pub fn new(data_dir: PathBuf) -> Option<Self> {
        let providers_dir = data_dir.join("schemas").join("providers");
        if !providers_dir.is_dir() {
            return None;
        }

        let mut registry = HashMap::new();
        for entry in std::fs::read_dir(&providers_dir).ok()? {
            let entry = match entry {
                Ok(e) => e,
                Err(_) => continue,
            };
            let path = entry.path();
            if path.extension().and_then(|e| e.to_str()) != Some("json") {
                continue;
            }
            let region = match path.file_stem().and_then(|s| s.to_str()) {
                Some(s) => s.replace('_', "-"),
                None => continue,
            };
            let content = match std::fs::read_to_string(&path) {
                Ok(c) => c,
                Err(_) => continue,
            };
            let map: HashMap<String, String> = match serde_json::from_str(&content) {
                Ok(m) => m,
                Err(_) => continue,
            };
            registry.insert(region, map);
        }

        // Load prefix schemas (resource-attributes, parameters, etc.)
        let mut prefix_schemas = HashMap::new();
        let attrs_dir = data_dir.join("schemas").join("resource-attributes");
        if let Ok(entries) = std::fs::read_dir(&attrs_dir) {
            for entry in entries.flatten() {
                let path = entry.path();
                if let Some(name) = path.file_stem().and_then(|s| s.to_str()) {
                    if let Ok(content) = std::fs::read_to_string(&path) {
                        if let Ok(val) = serde_json::from_str(&content) {
                            prefix_schemas.insert(name.to_string(), val);
                        }
                    }
                }
            }
        }

        // Load other schemas (parameters, template, etc.)
        let other_dir = data_dir.join("schemas").join("other");
        if let Ok(entries) = std::fs::read_dir(&other_dir) {
            for entry in entries.flatten() {
                let path = entry.path();
                if path.is_dir() {
                    // Load all JSON files in subdirectories
                    if let Ok(sub_entries) = std::fs::read_dir(&path) {
                        for sub_entry in sub_entries.flatten() {
                            let sub_path = sub_entry.path();
                            if let Some(name) = sub_path.file_stem().and_then(|s| s.to_str()) {
                                let dir_name = path.file_name().and_then(|s| s.to_str()).unwrap_or("");
                                let key = format!("{}/{}", dir_name, name);
                                if let Ok(content) = std::fs::read_to_string(&sub_path) {
                                    if let Ok(val) = serde_json::from_str(&content) {
                                        prefix_schemas.insert(key, val);
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

        // Load SAM provider mapping
        let sam_registry: HashMap<String, String> = std::fs::read_to_string(
            data_dir.join("schemas").join("sam").join("provider.json"),
        )
        .ok()
        .and_then(|c| serde_json::from_str(&c).ok())
        .unwrap_or_default();

        Some(Self {
            data_dir,
            registry,
            sam_registry,
            cache: std::sync::RwLock::new(HashMap::new()),
            prefix_schemas,
        })
    }

    fn load_resource_schema(&self, hash: &str, resource_type: &str) -> Option<ResourceSchema> {
        let path = self.data_dir.join("schemas").join("resources").join(format!("{}.json", hash));
        let sam_path = self.data_dir.join("schemas").join("sam").join(format!("{}.json", hash));
        let content = std::fs::read_to_string(&path)
            .or_else(|_| std::fs::read_to_string(&sam_path))
            .ok()?;
        let raw: serde_json::Value = serde_json::from_str(&content).ok()?;
        Some(parse_resource_schema(resource_type, raw))
    }

    fn get_cached_schema(&self, resource_type: &str, region: &str) -> Option<&ResourceSchema> {
        let hash = self.registry.get(region)?.get(resource_type)
            .or_else(|| {
                if resource_type.starts_with("AWS::Serverless::") {
                    self.sam_registry.get(resource_type)
                } else {
                    None
                }
            })?;
        {
            let cache = self.cache.read().ok()?;
            if let Some(schema) = cache.get(hash) {
                // SAFETY: Box provides a stable heap address. We never remove entries
                // from the cache, so the pointee lives as long as `self`.
                let ptr: *const ResourceSchema = &**schema;
                return Some(unsafe { &*ptr });
            }
        }
        let schema = self.load_resource_schema(hash, resource_type)?;
        let mut cache = self.cache.write().ok()?;
        let entry = cache.entry(hash.clone()).or_insert_with(|| Box::new(schema));
        // SAFETY: Same as above — Box provides a stable heap address.
        let ptr: *const ResourceSchema = &**entry;
        Some(unsafe { &*ptr })
    }
}

impl SchemaProvider for BundledSchemaProvider {
    fn resolve(&self, path: &[&str], region: &str) -> Option<SchemaNode> {
        match path {
            // Resource entry attributes (Type, Properties, DependsOn, etc.)
            ["Resources", _, rest @ ..] if rest.is_empty() => {
                if let Some(res_schema) = self.prefix_schemas.get("resources/configuration") {
                    let res_def = res_schema.get("definitions")
                        .and_then(|d| d.get("ResourceConfiguration"));
                    if let Some(def) = res_def {
                        let node = parse_schema_node_with_defs(def, res_schema.get("definitions"));
                        return Some(node);
                    }
                    // Fallback: use patternProperties
                    let res_def = res_schema.get("patternProperties")
                        .and_then(|pp| pp.as_object())
                        .and_then(|pp| pp.values().next());
                    if let Some(def) = res_def {
                        return Some(parse_schema_node_with_defs(def, res_schema.get("definitions")));
                    }
                }
                None
            }
            ["Resources", resource_type, "Properties", rest @ ..] => {
                let schema = self.get_cached_schema(resource_type, region)?;
                navigate_schema_node(&schema.root, rest)
            }
            ["Resources", _resource_type, attr, rest @ ..] => {
                // UpdatePolicy, CreationPolicy, etc.
                let prefix_schema = self.prefix_schemas.get(*attr)?;
                let node = parse_schema_node(prefix_schema);
                navigate_schema_node(&node, rest)
            }
            ["Parameters", _, rest @ ..] => {
                if let Some(param_schema) = self.prefix_schemas.get("parameters/configuration") {
                    let param_def = param_schema.get("patternProperties")
                        .and_then(|pp| pp.as_object())
                        .and_then(|pp| pp.values().next());
                    if let Some(def) = param_def {
                        // Always build synthetic node — the if/then/else schema
                        // doesn't parse cleanly into properties + allowed_values
                        let mut props = IndexMap::new();
                        collect_property_names(def, &mut props);
                        collect_type_enum(def, &mut props);
                        let mut synth = empty_schema_node();
                        synth.schema_type = vec!["object".to_string()];
                        synth.properties = props;
                        synth.required = vec!["Type".to_string()];
                        synth.raw = def.clone();
                        return navigate_schema_node(&synth, rest);
                    }
                }
                None
            }
            ["Outputs", _, rest @ ..] => {
                let node = output_schema_node();
                navigate_schema_node(&node, rest)
            }
            ["Conditions", _, rest @ ..] => {
                let node = condition_schema_node();
                navigate_schema_node(&node, rest)
            }
            ["Transform", rest @ ..] => {
                let transforms_schema = self.prefix_schemas.get("transforms/configuration")?;
                let node = parse_schema_node(transforms_schema);
                navigate_schema_node(&node, rest)
            }
            // Template-level: resolve top-level keys
            [key] => {
                let template_schema = self.prefix_schemas.get("template/template")?;
                let props = template_schema.get("properties")?;
                let key_schema = props.get(*key)?;
                Some(parse_schema_node(key_schema))
            }
            _ => None,
        }
    }

    fn get_resource_schema(&self, resource_type: &str, region: &str) -> Option<&ResourceSchema> {
        self.get_cached_schema(resource_type, region)
    }

    fn get_template_schema(&self) -> Option<&serde_json::Value> {
        self.prefix_schemas.get("template/template")
    }

    fn get_other_schema(&self, path: &str) -> Option<&serde_json::Value> {
        self.prefix_schemas.get(path)
    }

    fn resource_types(&self, region: &str) -> Vec<String> {
        let mut types: Vec<String> = self.registry
            .get(region)
            .map(|m| m.keys().cloned().collect())
            .unwrap_or_default();
        types.extend(self.sam_registry.keys().cloned());
        types
    }

    fn schemas_for_regions<'a>(
        &'a self,
        resource_type: &str,
        regions: &'a [String],
    ) -> Vec<(&'a ResourceSchema, Vec<&'a str>)> {
        let mut hash_to_regions: IndexMap<&str, Vec<&str>> = IndexMap::new();
        for region in regions {
            let hash = self.registry.get(region.as_str()).and_then(|m| m.get(resource_type))
                .or_else(|| {
                    if resource_type.starts_with("AWS::Serverless::") {
                        self.sam_registry.get(resource_type)
                    } else {
                        None
                    }
                });
            if let Some(hash) = hash {
                hash_to_regions.entry(hash.as_str()).or_default().push(region.as_str());
            }
        }
        hash_to_regions
            .into_iter()
            .filter_map(|(_hash, region_list)| {
                let schema = self.get_resource_schema(resource_type, region_list[0])?;
                Some((schema, region_list))
            })
            .collect()
    }
}

pub fn navigate_schema_node(node: &SchemaNode, path: &[&str]) -> Option<SchemaNode> {
    if path.is_empty() {
        return Some(node.clone());
    }

    // "*" or numeric index means descend into array items
    if path[0] == "*" || path[0].parse::<usize>().is_ok() {
        if let Some(ref items) = node.items {
            return navigate_schema_node(items, &path[1..]);
        }
        // For objects with patternProperties, the node itself is the wildcard
        return navigate_schema_node(node, &path[1..]);
    }

    // If current node is an array, auto-descend into items
    if node.schema_type.contains(&"array".to_string()) {
        if let Some(ref items) = node.items {
            return navigate_schema_node(items, path);
        }
    }

    if let Some(child) = node.properties.get(path[0]) {
        return navigate_schema_node(child, &path[1..]);
    }

    use std::sync::{LazyLock, Mutex};
    use std::collections::HashMap as StdHashMap;
    static REGEX_CACHE: LazyLock<Mutex<StdHashMap<String, regex::Regex>>> =
        LazyLock::new(|| Mutex::new(StdHashMap::new()));

    for (pattern, schema) in &node.pattern_properties {
        let matches = {
            let mut cache = REGEX_CACHE.lock().unwrap();
            let re = cache.entry(pattern.clone()).or_insert_with(|| {
                regex::Regex::new(pattern).unwrap_or_else(|_| regex::Regex::new("^$").unwrap())
            });
            re.is_match(path[0])
        };
        if matches {
            return navigate_schema_node(schema, &path[1..]);
        }
    }

    None
}

pub fn parse_schema_node(raw: &serde_json::Value) -> SchemaNode {
    parse_schema_node_with_defs(raw, None)
}

pub fn parse_schema_node_with_defs(raw: &serde_json::Value, definitions: Option<&serde_json::Value>) -> SchemaNode {
    parse_schema_node_impl(raw, definitions, 0)
}

const MAX_REF_DEPTH: u16 = 50;

fn parse_schema_node_impl(raw: &serde_json::Value, definitions: Option<&serde_json::Value>, depth: u16) -> SchemaNode {
    if depth > MAX_REF_DEPTH {
        return empty_schema_node();
    }

    // Resolve $ref
    if let Some(ref_path) = raw.get("$ref").and_then(|v| v.as_str()) {
        if let Some(resolved) = resolve_ref(ref_path, definitions) {
            return parse_schema_node_impl(resolved, definitions, depth + 1);
        }
    }

    // Type
    let schema_type = match raw.get("type") {
        Some(serde_json::Value::String(s)) => vec![s.clone()],
        Some(serde_json::Value::Array(arr)) => {
            arr.iter().filter_map(|v| v.as_str().map(String::from)).collect()
        }
        _ => vec![],
    };

    // Object keywords
    let mut properties = IndexMap::new();
    if let Some(props) = raw.get("properties").and_then(|v| v.as_object()) {
        for (name, prop_raw) in props {
            properties.insert(name.clone(), parse_schema_node_impl(prop_raw, definitions, depth + 1));
        }
    }

    let required: Vec<String> = raw
        .get("required")
        .and_then(|v| v.as_array())
        .map(|arr| arr.iter().filter_map(|v| v.as_str().map(String::from)).collect())
        .unwrap_or_default();

    let additional_properties = raw.get("additionalProperties").map(|v| {
        match v {
            serde_json::Value::Bool(b) => AdditionalProperties::Bool(*b),
            _ => AdditionalProperties::Schema(Box::new(parse_schema_node_impl(v, definitions, depth + 1))),
        }
    });

    let pattern_properties: Vec<(String, SchemaNode)> = raw
        .get("patternProperties")
        .and_then(|v| v.as_object())
        .map(|obj| {
            obj.iter()
                .map(|(pat, schema)| (pat.clone(), parse_schema_node_impl(schema, definitions, depth + 1)))
                .collect()
        })
        .unwrap_or_default();

    let dependent_required: IndexMap<String, Vec<String>> = raw
        .get("dependentRequired")
        .and_then(|v| v.as_object())
        .map(|obj| {
            obj.iter()
                .map(|(k, v)| {
                    let deps = v.as_array()
                        .map(|arr| arr.iter().filter_map(|s| s.as_str().map(String::from)).collect())
                        .unwrap_or_default();
                    (k.clone(), deps)
                })
                .collect()
        })
        .unwrap_or_default();

    let dependent_excluded: IndexMap<String, Vec<String>> = raw
        .get("dependentExcluded")
        .and_then(|v| v.as_object())
        .map(|obj| {
            obj.iter()
                .map(|(k, v)| {
                    let deps = v.as_array()
                        .map(|arr| arr.iter().filter_map(|s| s.as_str().map(String::from)).collect())
                        .unwrap_or_default();
                    (k.clone(), deps)
                })
                .collect()
        })
        .unwrap_or_default();

    let max_properties = raw.get("maxProperties").and_then(|v| v.as_u64());
    let min_properties = raw.get("minProperties").and_then(|v| v.as_u64());

    let property_names = raw.get("propertyNames")
        .map(|v| Box::new(parse_schema_node_impl(v, definitions, depth + 1)));

    let required_xor: Option<Vec<String>> = raw
        .get("requiredXor")
        .and_then(|v| v.as_array())
        .map(|arr| arr.iter().filter_map(|v| v.as_str().map(String::from)).collect());

    let required_or: Option<Vec<String>> = raw
        .get("requiredOr")
        .and_then(|v| v.as_array())
        .map(|arr| arr.iter().filter_map(|v| v.as_str().map(String::from)).collect());

    // Array keywords
    let items = raw.get("items").map(|i| Box::new(parse_schema_node_impl(i, definitions, depth + 1)));
    let min_items = raw.get("minItems").and_then(|v| v.as_u64());
    let max_items = raw.get("maxItems").and_then(|v| v.as_u64());
    let unique_items = raw.get("uniqueItems").and_then(|v| v.as_bool());
    let unique_keys: Option<Vec<String>> = raw
        .get("uniqueKeys")
        .and_then(|v| v.as_array())
        .map(|arr| arr.iter().filter_map(|v| v.as_str().map(String::from)).collect());
    let max_unique_items = raw.get("maxUniqueItems").and_then(|v| v.as_u64());
    let prefix_items: Vec<SchemaNode> = raw
        .get("prefixItems")
        .and_then(|v| v.as_array())
        .map(|arr| arr.iter().map(|v| parse_schema_node_impl(v, definitions, depth + 1)).collect())
        .unwrap_or_default();
    let contains = raw.get("contains")
        .map(|v| Box::new(parse_schema_node_impl(v, definitions, depth + 1)));

    // String keywords
    let pattern = raw.get("pattern").and_then(|v| v.as_str()).map(String::from);
    let min_length = raw.get("minLength").and_then(|v| v.as_u64());
    let max_length = raw.get("maxLength").and_then(|v| v.as_u64());
    let format = raw.get("format").and_then(|v| v.as_str()).map(String::from);

    // Numeric keywords
    let minimum = raw.get("minimum").and_then(|v| v.as_f64());
    let maximum = raw.get("maximum").and_then(|v| v.as_f64());
    let exclusive_minimum = raw.get("exclusiveMinimum").and_then(|v| v.as_f64());
    let exclusive_maximum = raw.get("exclusiveMaximum").and_then(|v| v.as_f64());
    let multiple_of = raw.get("multipleOf").and_then(|v| v.as_f64());

    // Value keywords
    let enum_values = raw.get("enum").and_then(|v| v.as_array()).map(|arr| arr.clone());
    let enum_case_insensitive: Option<Vec<String>> = raw
        .get("enumCaseInsensitive")
        .and_then(|v| v.as_array())
        .map(|arr| arr.iter().filter_map(|v| v.as_str().map(String::from)).collect());
    let const_value = raw.get("const").cloned();

    // Composition keywords
    let all_of: Vec<SchemaNode> = raw
        .get("allOf")
        .and_then(|v| v.as_array())
        .map(|arr| arr.iter().map(|v| parse_schema_node_impl(v, definitions, depth + 1)).collect())
        .unwrap_or_default();
    let any_of: Vec<SchemaNode> = raw
        .get("anyOf")
        .and_then(|v| v.as_array())
        .map(|arr| arr.iter().map(|v| parse_schema_node_impl(v, definitions, depth + 1)).collect())
        .unwrap_or_default();
    let one_of: Vec<SchemaNode> = raw
        .get("oneOf")
        .and_then(|v| v.as_array())
        .map(|arr| arr.iter().map(|v| parse_schema_node_impl(v, definitions, depth + 1)).collect())
        .unwrap_or_default();
    let not = raw.get("not")
        .map(|v| Box::new(parse_schema_node_impl(v, definitions, depth + 1)));
    let if_schema = raw.get("if")
        .map(|v| Box::new(parse_schema_node_impl(v, definitions, depth + 1)));
    let then_schema = raw.get("then")
        .map(|v| Box::new(parse_schema_node_impl(v, definitions, depth + 1)));
    let else_schema = raw.get("else")
        .map(|v| Box::new(parse_schema_node_impl(v, definitions, depth + 1)));

    // IDE
    let description = raw.get("description").and_then(|v| v.as_str()).map(String::from);

    // CFN extensions
    let cfn_lint = raw.get("cfnLint").cloned();

    SchemaNode {
        schema_type,
        properties,
        required,
        additional_properties,
        pattern_properties,
        dependent_required,
        dependent_excluded,
        max_properties,
        min_properties,
        property_names,
        required_xor,
        required_or,
        items,
        min_items,
        max_items,
        unique_items,
        unique_keys,
        max_unique_items,
        prefix_items,
        contains,
        pattern,
        min_length,
        max_length,
        format,
        minimum,
        maximum,
        exclusive_minimum,
        exclusive_maximum,
        multiple_of,
        enum_values,
        enum_case_insensitive,
        const_value,
        all_of,
        any_of,
        one_of,
        not,
        if_schema,
        then_schema,
        else_schema,
        description,
        read_only: false,
        cfn_lint,
        raw: raw.clone(),
    }
}

pub fn empty_schema_node() -> SchemaNode {
    SchemaNode {
        schema_type: vec![],
        properties: IndexMap::new(),
        required: vec![],
        additional_properties: None,
        pattern_properties: vec![],
        dependent_required: IndexMap::new(),
        dependent_excluded: IndexMap::new(),
        max_properties: None,
        min_properties: None,
        property_names: None,
        required_xor: None,
        required_or: None,
        items: None,
        min_items: None,
        max_items: None,
        unique_items: None,
        unique_keys: None,
        max_unique_items: None,
        prefix_items: vec![],
        contains: None,
        pattern: None,
        min_length: None,
        max_length: None,
        format: None,
        minimum: None,
        maximum: None,
        exclusive_minimum: None,
        exclusive_maximum: None,
        multiple_of: None,
        enum_values: None,
        enum_case_insensitive: None,
        const_value: None,
        all_of: vec![],
        any_of: vec![],
        one_of: vec![],
        not: None,
        if_schema: None,
        then_schema: None,
        else_schema: None,
        description: None,
        read_only: false,
        cfn_lint: None,
        raw: serde_json::Value::Null,
    }
}

pub fn output_schema_node() -> SchemaNode {
    let mut props = IndexMap::new();
    let mut value_node = empty_schema_node();
    value_node.description = Some("The value of the property returned by the aws cloudformation describe-stacks command.".to_string());
    props.insert("Value".to_string(), value_node);

    let mut desc_node = empty_schema_node();
    desc_node.schema_type = vec!["string".to_string()];
    desc_node.description = Some("A String type that describes the output value.".to_string());
    props.insert("Description".to_string(), desc_node);

    let mut cond_node = empty_schema_node();
    cond_node.schema_type = vec!["string".to_string()];
    cond_node.description = Some("The name of a condition to associate with this output.".to_string());
    props.insert("Condition".to_string(), cond_node);

    let mut export_node = empty_schema_node();
    let mut name_node = empty_schema_node();
    name_node.schema_type = vec!["string".to_string()];
    name_node.description = Some("The name of the resource output to be exported for cross-stack reference.".to_string());
    export_node.properties.insert("Name".to_string(), name_node);
    props.insert("Export".to_string(), export_node);

    let mut node = empty_schema_node();
    node.schema_type = vec!["object".to_string()];
    node.properties = props;
    node.required = vec!["Value".to_string()];
    node
}

pub fn condition_schema_node() -> SchemaNode {
    // Conditions are intrinsic function expressions — no fixed properties
    // Return an empty object; completion for condition functions is handled separately
    empty_schema_node()
}

pub fn resolve_ref<'a>(ref_path: &str, definitions: Option<&'a serde_json::Value>) -> Option<&'a serde_json::Value> {
    // Handle "#/definitions/Foo"
    let name = ref_path.strip_prefix("#/definitions/")?;
    definitions?.get(name)
}

/// Recursively collect all propertyNames enum values from if/then/else structures.
pub fn collect_property_names(val: &serde_json::Value, props: &mut IndexMap<String, SchemaNode>) {
    if let Some(pn) = val.get("propertyNames").and_then(|v| v.get("enum")).and_then(|v| v.as_array()) {
        for name in pn.iter().filter_map(|v| v.as_str()) {
            if !props.contains_key(name) {
                let mut node = empty_schema_node();
                node.schema_type = vec!["string".to_string()];
                props.insert(name.to_string(), node);
            }
        }
    }
    for key in &["if", "then", "else"] {
        if let Some(child) = val.get(key) {
            collect_property_names(child, props);
        }
    }
}

/// Collect all Type enum/const values from if/then/else structures.
pub fn collect_type_enum(val: &serde_json::Value, props: &mut IndexMap<String, SchemaNode>) {
    let mut types = std::collections::BTreeSet::new();
    collect_type_values(val, &mut types);
    if !types.is_empty() {
        let mut node = empty_schema_node();
        node.schema_type = vec!["string".to_string()];
        node.description = Some("The data type for the parameter.".to_string());
        let type_strings: Vec<String> = types.into_iter().collect();
        node.enum_values = Some(type_strings.iter().map(|s| serde_json::Value::String(s.clone())).collect());
        props.insert("Type".to_string(), node);
    }
}

pub fn collect_type_values(val: &serde_json::Value, types: &mut std::collections::BTreeSet<String>) {
    if let Some(props) = val.get("properties").and_then(|v| v.get("Type")) {
        if let Some(c) = props.get("const").and_then(|v| v.as_str()) {
            types.insert(c.to_string());
        }
        if let Some(arr) = props.get("enum").and_then(|v| v.as_array()) {
            for v in arr.iter().filter_map(|v| v.as_str()) {
                types.insert(v.to_string());
            }
        }
    }
    for key in &["if", "then", "else"] {
        if let Some(child) = val.get(key) {
            collect_type_values(child, types);
        }
    }
}

pub fn parse_resource_schema(resource_type: &str, raw: serde_json::Value) -> ResourceSchema {
    let description = raw.get("description").and_then(|v| v.as_str()).map(String::from);

    let read_only_paths: Vec<String> = raw
        .get("readOnlyProperties")
        .and_then(|v| v.as_array())
        .map(|arr| {
            arr.iter()
                .filter_map(|v| v.as_str())
                .filter_map(|s| s.strip_prefix("/properties/"))
                .map(String::from)
                .collect()
        })
        .unwrap_or_default();

    let definitions = raw.get("definitions");
    let mut root = parse_schema_node_with_defs(&raw, definitions);

    // Mark read-only properties
    for path in &read_only_paths {
        let segments: Vec<&str> = path.split('/').collect();
        let mut current = &mut root;
        let mut found = true;
        for (i, seg) in segments.iter().enumerate() {
            if i == segments.len() - 1 {
                if let Some(prop) = current.properties.get_mut(*seg) {
                    prop.read_only = true;
                }
            } else if let Some(prop) = current.properties.get_mut(*seg) {
                current = prop;
            } else {
                found = false;
                break;
            }
        }
        let _ = found;
    }

    // Mark required properties
    let required: Vec<String> = raw
        .get("required")
        .and_then(|v| v.as_array())
        .map(|arr| arr.iter().filter_map(|v| v.as_str().map(String::from)).collect())
        .unwrap_or_default();
    root.required = required;

    ResourceSchema {
        resource_type: resource_type.to_string(),
        description,
        root,
        read_only_paths,
        raw,
    }
}

/// Returns the OS-standard cache directory for cfn-lsp schemas.
/// macOS: ~/Library/Caches/cfn-lsp/schemas
/// Linux: ~/.cache/cfn-lsp/schemas
/// Windows: %LOCALAPPDATA%\cfn-lsp\cache\schemas
pub fn default_cache_dir() -> Option<std::path::PathBuf> {
    dirs::cache_dir().map(|d| d.join("cfn-lsp").join("schemas"))
}

/// Embedded schema archive (compressed tar.gz).
#[cfg(feature = "bundled")]
static BUNDLED_SCHEMAS: &[u8] = include_bytes!("../data/bundled/schemas.tar.gz");

/// Extract bundled schemas to the cache directory if not already populated.
/// Returns the cache directory path.
#[cfg(feature = "bundled")]
pub fn extract_bundled_schemas() -> Option<PathBuf> {
    let cache_dir = default_cache_dir()?;
    let providers_dir = cache_dir.join("schemas").join("providers");

    // Already extracted?
    if providers_dir.is_dir() {
        if let Ok(entries) = std::fs::read_dir(&providers_dir) {
            if entries.count() > 0 {
                return Some(cache_dir);
            }
        }
    }

    // Extract
    use flate2::read::GzDecoder;
    use tar::Archive;

    let decoder = GzDecoder::new(BUNDLED_SCHEMAS);
    let mut archive = Archive::new(decoder);

    if let Err(e) = std::fs::create_dir_all(&cache_dir) {
        eprintln!("Failed to create cache dir: {}", e);
        return None;
    }

    if let Err(e) = archive.unpack(&cache_dir) {
        eprintln!("Failed to extract bundled schemas: {}", e);
        return None;
    }

    Some(cache_dir)
}

/// Reads/writes schemas from the OS cache directory.
/// Same on-disk format as BundledProvider (providers/*.json + resources/*.json).
pub struct CacheProvider {
    inner: Option<BundledSchemaProvider>,
    cache_dir: PathBuf,
    /// Directory containing JSON patches to apply at download time.
    patches_dir: Option<PathBuf>,
}

impl CacheProvider {
    pub fn new() -> Self {
        let cache_dir = default_cache_dir().unwrap_or_else(|| PathBuf::from(".cfn-lsp/schemas"));
        let inner = BundledSchemaProvider::new(cache_dir.clone());
        Self { inner, cache_dir, patches_dir: None }
    }

    pub fn from_dir(cache_dir: PathBuf) -> Self {
        let inner = BundledSchemaProvider::new(cache_dir.clone());
        Self { inner, cache_dir, patches_dir: None }
    }

    /// Set the patches directory for download-time patching.
    pub fn with_patches_dir(mut self, patches_dir: PathBuf) -> Self {
        self.patches_dir = Some(patches_dir);
        self
    }

    pub fn patches_dir(&self) -> Option<&std::path::Path> {
        self.patches_dir.as_deref()
    }

    pub fn cache_dir(&self) -> &std::path::Path {
        &self.cache_dir
    }

    /// Write a region mapping (type -> hash) to the cache.
    pub fn write_region(&self, region: &str, types: &HashMap<String, String>) -> std::io::Result<()> {
        let providers_dir = self.cache_dir.join("schemas").join("providers");
        std::fs::create_dir_all(&providers_dir)?;
        let filename = region.replace('-', "_") + ".json";
        let content = serde_json::to_string_pretty(types).map_err(|e| std::io::Error::new(std::io::ErrorKind::Other, e))?;
        std::fs::write(providers_dir.join(filename), content)
    }

    /// Write a schema to the cache by its hash.
    pub fn write_schema(&self, hash: &str, schema: &serde_json::Value) -> std::io::Result<()> {
        let resources_dir = self.cache_dir.join("schemas").join("resources");
        std::fs::create_dir_all(&resources_dir)?;
        let content = serde_json::to_string_pretty(schema).map_err(|e| std::io::Error::new(std::io::ErrorKind::Other, e))?;
        std::fs::write(resources_dir.join(format!("{}.json", hash)), content)
    }

    /// Check if a schema hash exists in the cache.
    pub fn has_schema(&self, hash: &str) -> bool {
        self.cache_dir.join("schemas").join("resources").join(format!("{}.json", hash)).exists()
    }

    /// Reload the inner provider after writing new data.
    pub fn reload(&mut self) {
        self.inner = BundledSchemaProvider::new(self.cache_dir.clone());
    }
}

impl SchemaProvider for CacheProvider {
    fn resolve(&self, path: &[&str], region: &str) -> Option<SchemaNode> {
        self.inner.as_ref()?.resolve(path, region)
    }
    fn get_resource_schema(&self, resource_type: &str, region: &str) -> Option<&ResourceSchema> {
        self.inner.as_ref()?.get_resource_schema(resource_type, region)
    }
    fn resource_types(&self, region: &str) -> Vec<String> {
        self.inner.as_ref().map(|p| p.resource_types(region)).unwrap_or_default()
    }
    fn schemas_for_regions<'a>(&'a self, resource_type: &str, regions: &'a [String]) -> Vec<(&'a ResourceSchema, Vec<&'a str>)> {
        self.inner.as_ref().map(|p| p.schemas_for_regions(resource_type, regions)).unwrap_or_default()
    }
    fn get_template_schema(&self) -> Option<&serde_json::Value> {
        self.inner.as_ref()?.get_template_schema()
    }
    fn get_other_schema(&self, path: &str) -> Option<&serde_json::Value> {
        self.inner.as_ref()?.get_other_schema(path)
    }
}

/// Downloads schemas from the public CloudFormation schema endpoint.
/// Individual schemas: https://schema.cloudformation.{region}.amazonaws.com/{type-lowered-dashed}.json
/// Uses ETag from HTTP response as the version key for caching and dedup.
#[cfg(feature = "fetch")]
pub struct S3Provider {
    cache: CacheProvider,
}

#[cfg(feature = "fetch")]
fn schema_base_url(region: &str) -> String {
    let suffix = if region.starts_with("cn-") { ".cn" } else { "" };
    format!("https://schema.cloudformation.{}.amazonaws.com{}", region, suffix)
}

#[cfg(feature = "fetch")]
fn type_to_filename(type_name: &str) -> String {
    format!("{}.json", type_name.to_lowercase().replace("::", "-"))
}

#[cfg(feature = "fetch")]
fn clean_schema(raw: &mut serde_json::Value) {
    if let Some(obj) = raw.as_object_mut() {
        obj.remove("handlers");
        if let Some(tagging) = obj.get_mut("tagging").and_then(|t| t.as_object_mut()) {
            tagging.remove("permissions");
        }
    }
}

#[cfg(feature = "fetch")]
fn parse_etag(header: &str) -> String {
    header.trim_matches('"').to_string()
}

/// Simple 16-char hex hash for content-addressable storage.
#[cfg(feature = "fetch")]
fn content_hash(data: &[u8]) -> u128 {
    // FNV-1a 128-bit — fast, non-crypto, good distribution
    let mut hash: u128 = 0x6c62272e07bb0142_62b821756295c58d;
    for &byte in data {
        hash ^= byte as u128;
        hash = hash.wrapping_mul(0x0000000001000000_000000000000013B);
    }
    hash
}

#[cfg(feature = "fetch")]
impl S3Provider {
    pub fn new(cache: CacheProvider) -> Self {
        Self { cache }
    }

    /// Consume the S3Provider and return the inner CacheProvider.
    pub fn into_cache(self) -> CacheProvider {
        self.cache
    }

    /// Fetch a single resource type schema. Uses ETag as version key.
    /// Returns true if schema was new or updated.
    pub fn fetch_type(&mut self, type_name: &str, region: &str) -> Result<bool, Box<dyn std::error::Error>> {
        let url = format!("{}/{}", schema_base_url(region), type_to_filename(type_name));
        let resp = ureq::get(&url).call()?;
        let etag = resp.headers().get("ETag")
            .and_then(|v| v.to_str().ok())
            .map(parse_etag)
            .unwrap_or_default();
        if etag.is_empty() {
            return Err("No ETag in response".into());
        }

        if !self.cache.has_schema(&etag) {
            let body = resp.into_body().read_to_string()?;
            let mut raw: serde_json::Value = serde_json::from_str(&body)?;
            clean_schema(&mut raw);
            // Apply patches at download time (matches Python cfn-lint behavior)
            if let Some(patches_dir) = self.cache.patches_dir() {
                crate::patch::apply_patches_for_type(&mut raw, patches_dir, type_name);
            }
            self.cache.write_schema(&etag, &raw)?;
        }

        self.update_region_mapping(type_name, &etag, region)
    }

    /// HEAD request to check current ETag without downloading.
    pub fn check_etag(&self, type_name: &str, region: &str) -> Result<Option<String>, Box<dyn std::error::Error>> {
        let url = format!("{}/{}", schema_base_url(region), type_to_filename(type_name));
        let resp = ureq::head(&url).call()?;
        Ok(resp.headers().get("ETag").and_then(|v| v.to_str().ok()).map(parse_etag))
    }

    fn update_region_mapping(&mut self, type_name: &str, etag: &str, region: &str) -> Result<bool, Box<dyn std::error::Error>> {
        let providers_dir = self.cache.cache_dir().join("schemas").join("providers");
        let filename = region.replace('-', "_") + ".json";
        let path = providers_dir.join(&filename);
        let mut type_map: HashMap<String, String> = if path.exists() {
            serde_json::from_str(&std::fs::read_to_string(&path)?).unwrap_or_default()
        } else {
            HashMap::new()
        };
        let changed = type_map.get(type_name).map(|s| s.as_str()) != Some(etag);
        if changed {
            type_map.insert(type_name.to_string(), etag.to_string());
            self.cache.write_region(region, &type_map)?;
            self.cache.reload();
        }
        Ok(changed)
    }

    /// Download all schemas from the CloudFormation zip archive.
    /// Returns the number of schemas written.
    pub fn fetch_all_from_zip(&mut self, region: &str) -> Result<usize, Box<dyn std::error::Error>> {
        use std::io::{Cursor, Read};

        let url = format!("{}/CloudformationSchema.zip", schema_base_url(region));
        let resp = ureq::get(&url).call()?;
        let body = resp.into_body().read_to_vec()?;

        let cursor = Cursor::new(body);
        let mut archive = zip::ZipArchive::new(cursor)?;

        let mut type_map: HashMap<String, String> = HashMap::new();
        let mut count = 0;

        for i in 0..archive.len() {
            let mut file = archive.by_index(i)?;
            if !file.name().ends_with(".json") {
                continue;
            }
            let mut content = String::new();
            file.read_to_string(&mut content)?;

            let mut schema: serde_json::Value = match serde_json::from_str(&content) {
                Ok(v) => v,
                Err(_) => continue,
            };

            let type_name = match schema.get("typeName").and_then(|v| v.as_str()) {
                Some(t) => t.to_string(),
                None => continue,
            };

            clean_schema(&mut schema);
            if let Some(patches_dir) = self.cache.patches_dir() {
                crate::patch::apply_patches_for_type(&mut schema, patches_dir, &type_name);
            }

            // Use content hash as the key (no ETag available from zip)
            let schema_bytes = serde_json::to_vec(&schema)?;
            let hash = format!("{:x}", content_hash(&schema_bytes));
            self.cache.write_schema(&hash, &schema)?;
            type_map.insert(type_name, hash);
            count += 1;
        }

        self.cache.write_region(region, &type_map)?;
        self.cache.reload();
        Ok(count)
    }
}

#[cfg(feature = "fetch")]
impl SchemaProvider for S3Provider {
    fn resolve(&self, path: &[&str], region: &str) -> Option<SchemaNode> {
        self.cache.resolve(path, region)
    }
    fn get_resource_schema(&self, resource_type: &str, region: &str) -> Option<&ResourceSchema> {
        self.cache.get_resource_schema(resource_type, region)
    }
    fn resource_types(&self, region: &str) -> Vec<String> {
        self.cache.resource_types(region)
    }
    fn schemas_for_regions<'a>(&'a self, resource_type: &str, regions: &'a [String]) -> Vec<(&'a ResourceSchema, Vec<&'a str>)> {
        self.cache.schemas_for_regions(resource_type, regions)
    }
}

/// Tries multiple providers in order. Returns the first successful result.
pub struct ChainProvider {
    providers: Vec<Box<dyn SchemaProvider>>,
}

impl ChainProvider {
    pub fn new(providers: Vec<Box<dyn SchemaProvider>>) -> Self {
        Self { providers }
    }
}

impl SchemaProvider for ChainProvider {
    fn resolve(&self, path: &[&str], region: &str) -> Option<SchemaNode> {
        self.providers.iter().find_map(|p| p.resolve(path, region))
    }
    fn get_resource_schema(&self, resource_type: &str, region: &str) -> Option<&ResourceSchema> {
        self.providers.iter().find_map(|p| p.get_resource_schema(resource_type, region))
    }
    fn resource_types(&self, region: &str) -> Vec<String> {
        // Merge from all providers, dedup
        let mut types = Vec::new();
        let mut seen = std::collections::HashSet::new();
        for p in &self.providers {
            for t in p.resource_types(region) {
                if seen.insert(t.clone()) {
                    types.push(t);
                }
            }
        }
        types
    }
    fn schemas_for_regions<'a>(&'a self, resource_type: &str, regions: &'a [String]) -> Vec<(&'a ResourceSchema, Vec<&'a str>)> {
        for p in &self.providers {
            let result = p.schemas_for_regions(resource_type, regions);
            if !result.is_empty() {
                return result;
            }
        }
        vec![]
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_bundled_schema_provider() {
        let data_dir = std::path::PathBuf::from(env!("CARGO_MANIFEST_DIR"))
            .join("../../")
            .join("target/debug/data");
        if !data_dir.join("schemas/providers").is_dir() {
            eprintln!("Skipping: no schema data at {:?}", data_dir);
            return;
        }
        let provider = BundledSchemaProvider::new(data_dir).unwrap();

        // Check resource types
        let types = provider.resource_types("us-east-1");
        assert!(types.len() > 100, "should have many resource types, got {}", types.len());
        assert!(types.contains(&"AWS::S3::Bucket".to_string()));

        // Resolve Properties path
        let node = provider.resolve(&["Resources", "AWS::S3::Bucket", "Properties"], "us-east-1");
        assert!(node.is_some(), "should resolve Properties path");
        let node = node.unwrap();
        eprintln!("S3 Bucket properties count: {}", node.properties.len());
        eprintln!("S3 Bucket property names: {:?}", node.properties.keys().collect::<Vec<_>>());
        assert!(node.properties.len() > 10, "S3 Bucket should have many properties, got {}", node.properties.len());
        assert!(node.properties.contains_key("BucketName"));

        // Resolve a specific property
        let bn = provider.resolve(&["Resources", "AWS::S3::Bucket", "Properties", "BucketName"], "us-east-1");
        assert!(bn.is_some(), "should resolve BucketName");
        let bn = bn.unwrap();
        assert!(bn.schema_type.contains(&"string".to_string()), "BucketName should be string type");

        // $ref resolution: VersioningConfiguration should have Status with enum
        let vc = provider.resolve(&["Resources", "AWS::S3::Bucket", "Properties", "VersioningConfiguration"], "us-east-1");
        assert!(vc.is_some(), "should resolve VersioningConfiguration");
        let vc = vc.unwrap();
        assert!(vc.properties.contains_key("Status"), "VC should have Status property, got: {:?}", vc.properties.keys().collect::<Vec<_>>());
        let status = &vc.properties["Status"];
        let vals = status.allowed_values();
        assert!(vals.is_some(), "Status should have enum values");
        let vals = vals.unwrap();
        assert!(vals.contains(&"Enabled".to_string()), "Status enum should contain Enabled, got: {:?}", vals);
    }
}
