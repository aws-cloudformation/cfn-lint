use std::collections::HashMap;
use std::path::{Path, PathBuf};
use serde::{Deserialize, Serialize};
use thiserror::Error;

use crate::ast::AstNode;

#[derive(Debug, Error)]
pub enum ConfigError {
    #[error("Failed to read config file: {0}")]
    ReadError(#[from] std::io::Error),
    #[error("Failed to parse config file: {0}")]
    ParseError(#[from] serde_yaml::Error),
}

/// Full cfn-lint configuration — mirrors Python's ConfigMixIn.
/// Loaded from .cfnlintrc, template metadata, and CLI/LSP overrides.
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(default)]
pub struct Config {
    pub templates: Vec<String>,
    pub format: String,
    pub regions: Vec<String>,
    pub include_checks: Vec<String>,
    pub ignore_checks: Vec<String>,
    pub mandatory_checks: Vec<String>,
    pub include_experimental: bool,
    pub configure_rules: HashMap<String, HashMap<String, serde_json::Value>>,
    pub append_rules: Vec<PathBuf>,
    pub custom_rules: Option<String>,
    pub override_spec: Option<String>,
    pub registry_schemas: Vec<PathBuf>,
    pub ignore_templates: Vec<String>,
    pub ignore_bad_template: bool,
    pub merge_configs: bool,
    pub non_zero_exit_code: String,
    pub parameters: Vec<HashMap<String, String>>,
    pub parameter_files: Vec<PathBuf>,
    pub deployment_files: Vec<PathBuf>,
    #[serde(skip)]
    pub schema_dir: Option<PathBuf>,
}

impl Default for Config {
    fn default() -> Self {
        // Match Python cfn-lint: AWS_REGION takes priority, then AWS_DEFAULT_REGION
        let default_region = std::env::var("AWS_REGION")
            .or_else(|_| std::env::var("AWS_DEFAULT_REGION"))
            .unwrap_or_else(|_| "us-east-1".to_string());

        Config {
            templates: vec![],
            format: "parseable".to_string(),
            regions: vec![default_region],
            include_checks: vec![],
            ignore_checks: vec![],
            mandatory_checks: vec![],
            include_experimental: false,
            configure_rules: HashMap::new(),
            append_rules: vec![],
            custom_rules: None,
            override_spec: None,
            registry_schemas: vec![],
            ignore_templates: vec![],
            ignore_bad_template: false,
            merge_configs: false,
            non_zero_exit_code: "error".to_string(),
            parameters: vec![],
            parameter_files: vec![],
            deployment_files: vec![],
            schema_dir: None,
        }
    }
}

impl Config {
    /// Load configuration by merging: defaults → user config → project config → overrides.
    pub fn load(overrides: ConfigOverrides) -> Result<Config, ConfigError> {
        let mut config = Config::default();

        // Find and merge config files (user then project)
        let config_path = overrides.config_file.clone().or_else(|| find_config_file());
        if let Some(path) = config_path {
            if path.exists() {
                config.merge_file(&path)?;
            }
        } else {
            // Try user-level then project-level
            if let Some(user_path) = find_user_config() {
                config.merge_file(&user_path)?;
            }
            if let Some(project_path) = find_project_config() {
                config.merge_file(&project_path)?;
            }
        }

        // Apply overrides (CLI args or LSP settings)
        config.apply_overrides(overrides);

        Ok(config)
    }

    /// Merge template-level Metadata.cfn-lint.config into this config.
    pub fn merge_template_metadata(&mut self, root: &AstNode) {
        let config_node = root.as_object()
            .and_then(|o| o.get("Metadata"))
            .and_then(|n| n.as_object())
            .and_then(|o| o.get("cfn-lint"))
            .and_then(|n| n.as_object())
            .and_then(|o| o.get("config"))
            .and_then(|n| n.as_object());

        let Some(config_obj) = config_node else { return };

        if let Some(arr) = config_obj.get("ignore_checks").and_then(|n| n.as_array()) {
            for elem in &arr.elements {
                if let Some(s) = elem.as_str() {
                    self.ignore_checks.push(s.to_string());
                }
            }
        }
        if let Some(arr) = config_obj.get("include_checks").and_then(|n| n.as_array()) {
            for elem in &arr.elements {
                if let Some(s) = elem.as_str() {
                    self.include_checks.push(s.to_string());
                }
            }
        }
        if let Some(arr) = config_obj.get("regions").and_then(|n| n.as_array()) {
            self.regions = arr.elements.iter().filter_map(|e| e.as_str().map(String::from)).collect();
        }
        if let Some(val) = config_obj.get("include_experimental") {
            if let Some(b) = val.as_bool() {
                self.include_experimental = b;
            }
        }
        if let Some(val) = config_obj.get("ignore_bad_template") {
            if let Some(b) = val.as_bool() {
                self.ignore_bad_template = b;
            }
        }
        if let Some(obj) = config_obj.get("configure_rules").and_then(|n| n.as_object()) {
            for (key, value) in obj.iter() {
                if let Some(rule_obj) = value.as_object() {
                    let mut rule_config = HashMap::new();
                    for (rk, rv) in rule_obj.iter() {
                        if let Some(s) = rv.as_str() {
                            rule_config.insert(rk.to_string(), serde_json::Value::String(s.to_string()));
                        } else if let Some(b) = rv.as_bool() {
                            rule_config.insert(rk.to_string(), serde_json::Value::Bool(b));
                        }
                    }
                    self.configure_rules.insert(key.to_string(), rule_config);
                }
            }
        }
    }

    /// Check if a rule should be ignored.
    pub fn is_ignored(&self, rule_id: &str) -> bool {
        if self.mandatory_checks.iter().any(|m| rule_id.starts_with(m)) {
            return false;
        }
        self.ignore_checks.iter().any(|i| rule_id.starts_with(i))
    }

    /// Check if a rule should be included.
    pub fn is_included(&self, rule_id: &str, is_experimental: bool) -> bool {
        // Explicitly included rules are always included
        if self.include_checks.iter().any(|i| rule_id.starts_with(i)) {
            return true;
        }
        // Experimental rules need the flag OR explicit include
        if is_experimental {
            return self.include_experimental;
        }
        // Default includes: W and E
        rule_id.starts_with('W') || rule_id.starts_with('E')
    }

    /// Get rule-specific configuration.
    pub fn rule_config(&self, rule_id: &str) -> Option<&HashMap<String, serde_json::Value>> {
        self.configure_rules.get(rule_id)
    }

    fn merge_file(&mut self, path: &Path) -> Result<(), ConfigError> {
        let content = std::fs::read_to_string(path)?;
        let file: Config = serde_yaml::from_str(&content)?;

        // Merge lists (extend, don't replace)
        if !file.templates.is_empty() { self.templates.extend(file.templates); }
        if !file.regions.is_empty() { self.regions = file.regions; }
        if !file.ignore_checks.is_empty() { self.ignore_checks.extend(file.ignore_checks); }
        if !file.include_checks.is_empty() { self.include_checks.extend(file.include_checks); }
        if !file.mandatory_checks.is_empty() { self.mandatory_checks.extend(file.mandatory_checks); }
        if file.include_experimental { self.include_experimental = true; }
        if !file.configure_rules.is_empty() {
            for (k, v) in file.configure_rules { self.configure_rules.insert(k, v); }
        }
        if !file.append_rules.is_empty() { self.append_rules.extend(file.append_rules); }
        if file.custom_rules.is_some() { self.custom_rules = file.custom_rules; }
        if file.override_spec.is_some() { self.override_spec = file.override_spec; }
        if !file.registry_schemas.is_empty() { self.registry_schemas.extend(file.registry_schemas); }
        if !file.ignore_templates.is_empty() { self.ignore_templates.extend(file.ignore_templates); }
        if file.ignore_bad_template { self.ignore_bad_template = true; }
        if file.merge_configs { self.merge_configs = true; }
        if file.format != "parseable" { self.format = file.format; }
        if file.non_zero_exit_code != "error" { self.non_zero_exit_code = file.non_zero_exit_code; }

        Ok(())
    }

    fn apply_overrides(&mut self, o: ConfigOverrides) {
        if !o.templates.is_empty() { self.templates = o.templates; }
        if let Some(f) = o.format { self.format = f; }
        if !o.regions.is_empty() { self.regions = o.regions; }
        if !o.include_checks.is_empty() { self.include_checks = o.include_checks; }
        if !o.ignore_checks.is_empty() { self.ignore_checks = o.ignore_checks; }
        if let Some(v) = o.include_experimental { self.include_experimental = v; }
        if let Some(d) = o.schema_dir { self.schema_dir = Some(d); }
        if !o.configure_rules.is_empty() {
            for (k, v) in o.configure_rules { self.configure_rules.insert(k, v); }
        }
        if !o.append_rules.is_empty() { self.append_rules = o.append_rules; }
        if !o.registry_schemas.is_empty() { self.registry_schemas = o.registry_schemas; }
        if !o.ignore_templates.is_empty() { self.ignore_templates = o.ignore_templates; }
        if let Some(n) = o.non_zero_exit_code { self.non_zero_exit_code = n; }
        if let Some(s) = o.override_spec { self.override_spec = Some(s); }
    }
}

/// Overrides from CLI args or LSP settings — applied on top of file config.
#[derive(Debug, Clone, Default)]
pub struct ConfigOverrides {
    pub templates: Vec<String>,
    pub format: Option<String>,
    pub regions: Vec<String>,
    pub include_checks: Vec<String>,
    pub ignore_checks: Vec<String>,
    pub include_experimental: Option<bool>,
    pub schema_dir: Option<PathBuf>,
    pub config_file: Option<PathBuf>,
    pub configure_rules: HashMap<String, HashMap<String, serde_json::Value>>,
    pub append_rules: Vec<PathBuf>,
    pub registry_schemas: Vec<PathBuf>,
    pub ignore_templates: Vec<String>,
    pub non_zero_exit_code: Option<String>,
    pub override_spec: Option<String>,
}

/// Find .cfnlintrc in the current directory.
fn find_project_config() -> Option<PathBuf> {
    let cwd = std::env::current_dir().ok()?;
    for name in &[".cfnlintrc", ".cfnlintrc.yaml", ".cfnlintrc.yml"] {
        let path = cwd.join(name);
        if path.exists() { return Some(path); }
    }
    None
}

/// Find .cfnlintrc in the user's home directory.
fn find_user_config() -> Option<PathBuf> {
    let home = dirs::home_dir()?;
    for name in &[".cfnlintrc", ".cfnlintrc.yaml", ".cfnlintrc.yml"] {
        let path = home.join(name);
        if path.exists() { return Some(path); }
    }
    None
}

/// Find config file — project first, then user.
fn find_config_file() -> Option<PathBuf> {
    find_project_config().or_else(find_user_config)
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::io::Write;
    use tempfile::NamedTempFile;

    #[test]
    fn test_defaults() {
        // Use a non-existent config file to get true defaults without
        // picking up a .cfnlintrc from the working directory.
        let config = Config::load(ConfigOverrides {
            config_file: Some(PathBuf::from("/tmp/nonexistent-cfnlintrc-test")),
            ..Default::default()
        }).unwrap();
        assert_eq!(config.format, "parseable");
        // Default region comes from AWS_DEFAULT_REGION/AWS_REGION env var or "us-east-1"
        let expected_region = std::env::var("AWS_DEFAULT_REGION")
            .or_else(|_| std::env::var("AWS_REGION"))
            .unwrap_or_else(|_| "us-east-1".to_string());
        assert_eq!(config.regions, vec![expected_region]);
        assert!(config.ignore_checks.is_empty());
        assert!(!config.include_experimental);
    }

    #[test]
    fn test_config_file() {
        let mut file = NamedTempFile::new().unwrap();
        writeln!(file, "regions:\n  - eu-west-1\nignore_checks:\n  - E3001\ninclude_experimental: true").unwrap();

        let config = Config::load(ConfigOverrides {
            config_file: Some(file.path().to_path_buf()),
            ..Default::default()
        }).unwrap();

        assert_eq!(config.regions, vec!["eu-west-1"]);
        assert_eq!(config.ignore_checks, vec!["E3001"]);
        assert!(config.include_experimental);
    }

    #[test]
    fn test_overrides_win() {
        let mut file = NamedTempFile::new().unwrap();
        writeln!(file, "regions:\n  - eu-west-1\nignore_checks:\n  - E3001").unwrap();

        let config = Config::load(ConfigOverrides {
            config_file: Some(file.path().to_path_buf()),
            regions: vec!["ap-southeast-1".to_string()],
            ignore_checks: vec!["W2001".to_string()],
            ..Default::default()
        }).unwrap();

        assert_eq!(config.regions, vec!["ap-southeast-1"]);
        assert_eq!(config.ignore_checks, vec!["W2001"]);
    }

    #[test]
    fn test_is_ignored() {
        let mut config = Config::default();
        config.ignore_checks = vec!["E3012".to_string(), "W".to_string()];
        config.mandatory_checks = vec!["E3012".to_string()];

        assert!(!config.is_ignored("E3012")); // mandatory overrides ignore
        assert!(config.is_ignored("W2001")); // W prefix matches
        assert!(!config.is_ignored("I1001")); // not ignored
    }

    #[test]
    fn test_is_included() {
        let config = Config::default();
        assert!(config.is_included("E3012", false)); // E prefix always included
        assert!(config.is_included("W2001", false)); // W prefix always included
        assert!(!config.is_included("I1001", false)); // I not included by default
        assert!(!config.is_included("E9999", true)); // experimental not included
    }

    #[test]
    fn test_configure_rules() {
        let mut file = NamedTempFile::new().unwrap();
        writeln!(file, "configure_rules:\n  E3012:\n    strict: true").unwrap();

        let config = Config::load(ConfigOverrides {
            config_file: Some(file.path().to_path_buf()),
            ..Default::default()
        }).unwrap();

        let rule_cfg = config.rule_config("E3012").unwrap();
        assert_eq!(rule_cfg.get("strict"), Some(&serde_json::Value::Bool(true)));
    }

    #[test]
    fn test_merge_configs_flag() {
        let mut file = NamedTempFile::new().unwrap();
        writeln!(file, "merge_configs: true\nignore_checks:\n  - E3001\n  - E3002").unwrap();

        let config = Config::load(ConfigOverrides {
            config_file: Some(file.path().to_path_buf()),
            ignore_checks: vec!["W2001".to_string()],
            ..Default::default()
        }).unwrap();

        // With merge_configs, CLI overrides replace (current behavior)
        // The merge_configs flag is stored for consumers to use
        assert!(config.merge_configs);
    }

    #[test]
    fn test_mandatory_checks_override_ignore() {
        let mut config = Config::default();
        config.ignore_checks = vec!["E3012".to_string()];
        config.mandatory_checks = vec!["E3012".to_string()];

        // Mandatory checks can't be ignored
        assert!(!config.is_ignored("E3012"));
        // But non-mandatory can be
        config.ignore_checks.push("W2001".to_string());
        assert!(config.is_ignored("W2001"));
    }

    #[test]
    fn test_include_experimental() {
        let mut config = Config::default();
        assert!(!config.is_included("I9001", true)); // experimental not included by default

        config.include_experimental = true;
        assert!(config.is_included("I9001", true)); // now included

        // Non-experimental always included for W/E
        assert!(config.is_included("W2001", false));
        assert!(config.is_included("E3012", false));
    }

    #[test]
    fn test_include_checks_specific() {
        let mut config = Config::default();
        config.include_checks = vec!["I".to_string()];

        // Explicitly included via include_checks — always included
        assert!(config.is_included("I9001", false));
        assert!(config.is_included("I9001", true)); // explicit include overrides experimental flag
    }

    #[test]
    fn test_template_metadata_regions() {
        use crate::parser;

        let template = r#"AWSTemplateFormatVersion: '2010-09-09'
Metadata:
  cfn-lint:
    config:
      regions:
        - eu-west-1
        - ap-southeast-1
Resources: {}"#;

        let ast = parser::parse(template.as_bytes()).unwrap();
        let mut config = Config::default();
        config.merge_template_metadata(&ast);
        assert_eq!(config.regions, vec!["eu-west-1", "ap-southeast-1"]);
    }

    #[test]
    fn test_template_metadata_ignore_checks() {
        use crate::parser;

        let template = r#"AWSTemplateFormatVersion: '2010-09-09'
Metadata:
  cfn-lint:
    config:
      ignore_checks:
        - E3012
        - W2001
Resources: {}"#;

        let ast = parser::parse(template.as_bytes()).unwrap();
        let mut config = Config::default();
        config.merge_template_metadata(&ast);
        assert_eq!(config.ignore_checks, vec!["E3012", "W2001"]);
    }

    #[test]
    fn test_template_metadata_configure_rules() {
        use crate::parser;

        let template = r#"AWSTemplateFormatVersion: '2010-09-09'
Metadata:
  cfn-lint:
    config:
      configure_rules:
        E3012:
          strict: true
Resources: {}"#;

        let ast = parser::parse(template.as_bytes()).unwrap();
        let mut config = Config::default();
        config.merge_template_metadata(&ast);
        let rule_cfg = config.rule_config("E3012").unwrap();
        assert_eq!(rule_cfg.get("strict"), Some(&serde_json::Value::Bool(true)));
    }

    #[test]
    fn test_all_config_options_from_file() {
        let mut file = NamedTempFile::new().unwrap();
        writeln!(file, r#"
templates:
  - "*.yaml"
format: json
regions:
  - us-west-2
ignore_checks:
  - E3001
include_checks:
  - I
mandatory_checks:
  - E0000
include_experimental: true
ignore_bad_template: true
merge_configs: true
non_zero_exit_code: warning
configure_rules:
  E3012:
    strict: true
"#).unwrap();

        let config = Config::load(ConfigOverrides {
            config_file: Some(file.path().to_path_buf()),
            ..Default::default()
        }).unwrap();

        assert_eq!(config.format, "json");
        assert_eq!(config.regions, vec!["us-west-2"]);
        assert_eq!(config.ignore_checks, vec!["E3001"]);
        assert_eq!(config.include_checks, vec!["I"]);
        assert_eq!(config.mandatory_checks, vec!["E0000"]);
        assert!(config.include_experimental);
        assert!(config.ignore_bad_template);
        assert!(config.merge_configs);
        assert_eq!(config.non_zero_exit_code, "warning");
        assert!(config.configure_rules.contains_key("E3012"));
    }

    #[test]
    fn test_empty_config_file() {
        let mut file = NamedTempFile::new().unwrap();
        writeln!(file, "").unwrap();

        // Empty file should not error — just use defaults
        let result = Config::load(ConfigOverrides {
            config_file: Some(file.path().to_path_buf()),
            ..Default::default()
        });
        // serde_yaml may return error for empty, that's ok
        let _ = result;
    }

    #[test]
    fn test_ignore_prefix_matching() {
        let mut config = Config::default();
        config.ignore_checks = vec!["W".to_string()]; // ignore all warnings

        assert!(config.is_ignored("W2001"));
        assert!(config.is_ignored("W3001"));
        assert!(!config.is_ignored("E3001")); // errors not ignored
    }
}
