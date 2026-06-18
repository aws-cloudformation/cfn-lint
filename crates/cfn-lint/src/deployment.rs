use std::collections::HashMap;
use std::path::Path;

/// A set of parameter values from a parameter file or deployment file.
#[derive(Debug, Clone)]
pub struct ParameterSet {
    pub source: String,
    pub parameters: HashMap<String, String>,
}

/// Parse a parameter file (CloudFormation CLI format).
/// Format: `[{"ParameterKey": "Name", "ParameterValue": "Value"}, ...]`
pub fn parse_parameter_file(path: &Path) -> Result<ParameterSet, String> {
    let content = std::fs::read_to_string(path)
        .map_err(|e| format!("Failed to read parameter file {}: {}", path.display(), e))?;

    let data: serde_json::Value = serde_json::from_str(&content)
        .map_err(|e| format!("Failed to parse parameter file {}: {}", path.display(), e))?;

    let arr = data.as_array()
        .ok_or_else(|| format!("Parameter file {} must be a JSON array", path.display()))?;

    let mut parameters = HashMap::new();
    for item in arr {
        let key = item.get("ParameterKey")
            .and_then(|v| v.as_str())
            .ok_or_else(|| format!("Missing ParameterKey in {}", path.display()))?;
        let value = item.get("ParameterValue")
            .and_then(|v| v.as_str())
            .ok_or_else(|| format!("Missing ParameterValue for {} in {}", key, path.display()))?;
        parameters.insert(key.to_string(), value.to_string());
    }

    Ok(ParameterSet {
        source: path.display().to_string(),
        parameters,
    })
}

/// Data extracted from a deployment file.
pub struct DeploymentFileData {
    pub template_file_path: String,
    pub parameters: HashMap<String, String>,
}

/// Parse a deployment file (git_sync format).
/// Format: `{template-file-path: "...", parameters: {...}, tags: {...}}`
pub fn parse_deployment_file(path: &Path) -> Result<DeploymentFileData, String> {
    let content = std::fs::read_to_string(path)
        .map_err(|e| format!("Failed to read deployment file {}: {}", path.display(), e))?;

    let data: serde_json::Value = if path.extension().map_or(false, |ext| ext == "json") {
        serde_json::from_str(&content)
            .map_err(|e| format!("Failed to parse deployment file {}: {}", path.display(), e))?
    } else {
        serde_yaml::from_str(&content)
            .map_err(|e| format!("Failed to parse deployment file {}: {}", path.display(), e))?
    };

    let obj = data.as_object()
        .ok_or_else(|| format!("Deployment file {} must be an object", path.display()))?;

    let template_file_path = obj.get("template-file-path")
        .and_then(|v| v.as_str())
        .ok_or_else(|| format!("Missing template-file-path in {}", path.display()))?
        .to_string();

    let mut parameters = HashMap::new();
    if let Some(params_obj) = obj.get("parameters").and_then(|v| v.as_object()) {
        for (key, value) in params_obj {
            let val_str = match value {
                serde_json::Value::String(s) => s.clone(),
                serde_json::Value::Number(n) => n.to_string(),
                serde_json::Value::Bool(b) => b.to_string(),
                _ => continue,
            };
            parameters.insert(key.clone(), val_str);
        }
    }

    Ok(DeploymentFileData {
        template_file_path,
        parameters,
    })
}

/// Expand deployment files into (template_path, parameter_set) pairs.
/// The template path is resolved relative to the deployment file's directory.
pub fn expand_deployment_files(
    deployment_files: &[std::path::PathBuf],
) -> Result<Vec<(String, ParameterSet)>, String> {
    let mut results = Vec::new();
    for path in deployment_files {
        let data = parse_deployment_file(path)?;
        let base_dir = path.parent().unwrap_or_else(|| Path::new("."));
        let template_path = base_dir.join(&data.template_file_path);
        let template_path = template_path.canonicalize()
            .unwrap_or(template_path)
            .display()
            .to_string();
        results.push((
            template_path,
            ParameterSet {
                source: path.display().to_string(),
                parameters: data.parameters,
            },
        ));
    }
    Ok(results)
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::io::Write;
    use tempfile::NamedTempFile;

    #[test]
    fn test_parse_parameter_file() {
        let mut f = NamedTempFile::new().unwrap();
        write!(f, r#"[
            {{"ParameterKey": "Env", "ParameterValue": "prod"}},
            {{"ParameterKey": "VpcId", "ParameterValue": "vpc-123"}}
        ]"#).unwrap();
        let result = parse_parameter_file(f.path()).unwrap();
        assert_eq!(result.parameters.get("Env"), Some(&"prod".to_string()));
        assert_eq!(result.parameters.get("VpcId"), Some(&"vpc-123".to_string()));
    }

    #[test]
    fn test_parse_deployment_file() {
        let mut f = NamedTempFile::with_suffix(".json").unwrap();
        write!(f, r#"{{
            "template-file-path": "templates/main.yaml",
            "parameters": {{"Env": "prod", "Count": 3}},
            "tags": {{"Team": "infra"}}
        }}"#).unwrap();
        let result = parse_deployment_file(f.path()).unwrap();
        assert_eq!(result.template_file_path, "templates/main.yaml");
        assert_eq!(result.parameters.get("Env"), Some(&"prod".to_string()));
        assert_eq!(result.parameters.get("Count"), Some(&"3".to_string()));
    }

    #[test]
    fn test_parse_parameter_file_invalid() {
        let mut f = NamedTempFile::new().unwrap();
        write!(f, "not json").unwrap();
        assert!(parse_parameter_file(f.path()).is_err());
    }
}
