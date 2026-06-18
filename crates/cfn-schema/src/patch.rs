//! Apply JSON patches to CloudFormation schemas at download time.
//!
//! Patches live in `data/patches/{providers,extensions}/{type_dir}/*.json`
//! and `data/patches/extensions/all/{type_dir}/*.json`.
//! Each file is an RFC 6902 JSON Patch array.

use std::path::Path;

/// Apply all patches for a resource type to a schema.
/// `patches_dir` is the root patches directory (e.g. `data/patches`).
/// `resource_type` is e.g. `"AWS::S3::Bucket"`.
pub fn apply_patches_for_type(
    schema: &mut serde_json::Value,
    patches_dir: &Path,
    resource_type: &str,
) {
    let type_dir = resource_type.to_lowercase().replace("::", "_");

    // Apply in same order as Python: providers first, then extensions
    apply_patches_from_dir(schema, &patches_dir.join("providers").join(&type_dir));
    apply_patches_from_dir(schema, &patches_dir.join("extensions").join(&type_dir));
    apply_patches_from_dir(
        schema,
        &patches_dir.join("extensions").join("all").join(&type_dir),
    );
}

fn apply_patches_from_dir(schema: &mut serde_json::Value, dir: &Path) {
    let entries = match std::fs::read_dir(dir) {
        Ok(e) => e,
        Err(_) => return,
    };
    let mut paths: Vec<_> = entries.filter_map(|e| e.ok()).map(|e| e.path()).collect();
    paths.sort();
    for path in paths {
        if path.extension().and_then(|e| e.to_str()) != Some("json") {
            continue;
        }
        let content = match std::fs::read_to_string(&path) {
            Ok(c) => c,
            Err(_) => continue,
        };
        let patch: json_patch::Patch = match serde_json::from_str(&content) {
            Ok(p) => p,
            Err(_) => continue,
        };
        if let Err(e) = json_patch::patch(schema, &patch) {
            eprintln!("warning: patch {} failed: {}", path.display(), e);
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;

    #[test]
    fn test_apply_patches_for_type() {
        let dir = tempfile::tempdir().unwrap();
        let patches_dir = dir.path().join("patches");

        // Create a provider patch
        let provider_dir = patches_dir.join("providers").join("aws_s3_bucket");
        fs::create_dir_all(&provider_dir).unwrap();
        fs::write(
            provider_dir.join("fix.json"),
            r#"[{"op": "add", "path": "/properties/Tag", "value": {"type": "string"}}]"#,
        )
        .unwrap();

        // Create an extension/all patch
        let ext_dir = patches_dir
            .join("extensions")
            .join("all")
            .join("aws_s3_bucket");
        fs::create_dir_all(&ext_dir).unwrap();
        fs::write(
            ext_dir.join("format.json"),
            r#"[{"op": "add", "path": "/properties/Name/format", "value": "AWS::S3::Bucket.Name"}]"#,
        ).unwrap();

        let mut schema = serde_json::json!({
            "properties": { "Name": { "type": "string" } }
        });

        apply_patches_for_type(&mut schema, &patches_dir, "AWS::S3::Bucket");

        assert_eq!(schema["properties"]["Tag"]["type"], "string");
        assert_eq!(
            schema["properties"]["Name"]["format"],
            "AWS::S3::Bucket.Name"
        );
    }

    #[test]
    fn test_missing_patches_dir_is_fine() {
        let mut schema = serde_json::json!({"properties": {}});
        apply_patches_for_type(&mut schema, Path::new("/nonexistent"), "AWS::S3::Bucket");
        assert_eq!(schema, serde_json::json!({"properties": {}}));
    }
}
