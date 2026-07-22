//! Apply JSON patches to all resource schemas on disk.
//!
//! Usage: patch-schemas <schemas-dir> <patches-dir>
//!
//! Reads type→hash mappings from `<schemas-dir>/providers/*.json`,
//! applies patches from `<patches-dir>`, and writes patched schemas
//! back to `<schemas-dir>/resources/`.

use std::collections::{HashMap, HashSet};
use std::path::{Path, PathBuf};

/// Apply all patches for `sorted_types` to the schema at `schema_path`, writing
/// the result back only if patching actually changed the schema.
///
/// Returns `true` if the file was rewritten, `false` otherwise (including when
/// the file is missing or unparseable — matching the caller's skip behavior).
///
/// Change detection compares the pre- and post-patch `serde_json::Value`s. An
/// earlier version compared the parsed `Value` against `schema.to_string()` (a
/// `String`); serde_json's `PartialEq<String> for Value` only matches the
/// `Value::String` variant, so an object schema was *never* equal to that
/// string and every file was rewritten on every run — producing spurious churn
/// across the vendored `data/schemas/` tree.
fn patch_one_schema(schema_path: &Path, patches_dir: &Path, sorted_types: &[&str]) -> bool {
    let content = match std::fs::read_to_string(schema_path) {
        Ok(c) => c,
        Err(_) => return false,
    };
    let mut schema: serde_json::Value = match serde_json::from_str(&content) {
        Ok(v) => v,
        Err(_) => return false,
    };

    let before = schema.clone();
    for rtype in sorted_types {
        cfn_schema::patch::apply_patches_for_type(&mut schema, patches_dir, rtype);
    }

    if schema != before {
        let out = serde_json::to_string_pretty(&schema).unwrap();
        std::fs::write(schema_path, out.as_bytes()).unwrap();
        true
    } else {
        false
    }
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    if args.len() != 3 {
        eprintln!("Usage: patch-schemas <schemas-dir> <patches-dir>");
        eprintln!(
            "  e.g. patch-schemas crates/cfn-lint/data/schemas crates/cfn-schema/data/patches"
        );
        std::process::exit(1);
    }

    let schemas_dir = PathBuf::from(&args[1]);
    let patches_dir = PathBuf::from(&args[2]);

    // Build hash → {resource_types} from all provider files
    let providers_dir = schemas_dir.join("providers");
    let mut hash_to_types: HashMap<String, HashSet<String>> = HashMap::new();

    for entry in std::fs::read_dir(&providers_dir).expect("cannot read providers dir") {
        let path = entry.unwrap().path();
        if path.extension().and_then(|e| e.to_str()) != Some("json") {
            continue;
        }
        let content = std::fs::read_to_string(&path).unwrap();
        let mapping: HashMap<String, String> = serde_json::from_str(&content).unwrap();
        for (rtype, hash) in mapping {
            hash_to_types.entry(hash).or_default().insert(rtype);
        }
    }

    eprintln!("Found {} unique schema hashes", hash_to_types.len());

    let mut patched_count = 0;
    let resources_dir = schemas_dir.join("resources");

    for (hash, types) in &hash_to_types {
        let schema_path = resources_dir.join(format!("{}.json", hash));
        let mut sorted_types: Vec<&str> = types.iter().map(String::as_str).collect();
        sorted_types.sort();
        if patch_one_schema(&schema_path, &patches_dir, &sorted_types) {
            patched_count += 1;
        }
    }

    eprintln!("Patched {} schemas", patched_count);
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;

    /// A no-op run (no applicable patches) must NOT rewrite the file. This
    /// guards the C9 regression: previously `schema != before` compared a
    /// `Value` against a `String` and was always true, rewriting every file.
    #[test]
    fn no_op_does_not_rewrite() {
        let dir = tempfile::tempdir().unwrap();
        let patches_dir = dir.path().join("patches");
        // No patches directory contents => nothing to apply.

        let schema_path = dir.path().join("abc123.json");
        // Deliberately compact (not pretty-printed) with a trailing marker, so
        // any rewrite via `to_string_pretty` would be observable.
        let original = r#"{"properties":{"Name":{"type":"string"}}}"#;
        fs::write(&schema_path, original).unwrap();

        let rewritten = patch_one_schema(&schema_path, &patches_dir, &["AWS::S3::Bucket"]);

        assert!(!rewritten, "no-op patch run should not report a rewrite");
        let after = fs::read_to_string(&schema_path).unwrap();
        assert_eq!(
            after, original,
            "file must be byte-for-byte unchanged when patching is a no-op"
        );
    }

    /// A run where a patch actually changes the schema MUST rewrite the file.
    #[test]
    fn applied_patch_rewrites() {
        let dir = tempfile::tempdir().unwrap();
        let patches_dir = dir.path().join("patches");
        let provider_dir = patches_dir.join("providers").join("aws_s3_bucket");
        fs::create_dir_all(&provider_dir).unwrap();
        fs::write(
            provider_dir.join("add-tag.json"),
            r#"[{"op": "add", "path": "/properties/Tag", "value": {"type": "string"}}]"#,
        )
        .unwrap();

        let schema_path = dir.path().join("def456.json");
        fs::write(&schema_path, r#"{"properties":{"Name":{"type":"string"}}}"#).unwrap();

        let rewritten = patch_one_schema(&schema_path, &patches_dir, &["AWS::S3::Bucket"]);

        assert!(rewritten, "an applied patch should report a rewrite");
        let after: serde_json::Value =
            serde_json::from_str(&fs::read_to_string(&schema_path).unwrap()).unwrap();
        assert_eq!(after["properties"]["Tag"]["type"], "string");
    }

    /// A patch that resolves to the same content is still a no-op: it must not
    /// rewrite. This proves change detection is by Value, not by presence of
    /// patch files.
    #[test]
    fn patch_producing_identical_schema_is_no_op() {
        let dir = tempfile::tempdir().unwrap();
        let patches_dir = dir.path().join("patches");
        let provider_dir = patches_dir.join("providers").join("aws_s3_bucket");
        fs::create_dir_all(&provider_dir).unwrap();
        // Add a property that already exists with the identical value.
        fs::write(
            provider_dir.join("noop.json"),
            r#"[{"op": "add", "path": "/properties/Name", "value": {"type": "string"}}]"#,
        )
        .unwrap();

        let schema_path = dir.path().join("ghi789.json");
        let original = r#"{"properties":{"Name":{"type":"string"}}}"#;
        fs::write(&schema_path, original).unwrap();

        let rewritten = patch_one_schema(&schema_path, &patches_dir, &["AWS::S3::Bucket"]);

        assert!(
            !rewritten,
            "patch yielding identical schema must be a no-op"
        );
        assert_eq!(fs::read_to_string(&schema_path).unwrap(), original);
    }

    /// Missing schema file is skipped without panicking and reports no rewrite.
    #[test]
    fn missing_file_is_skipped() {
        let dir = tempfile::tempdir().unwrap();
        let missing = dir.path().join("does-not-exist.json");
        assert!(!patch_one_schema(
            &missing,
            dir.path(),
            &["AWS::S3::Bucket"]
        ));
    }
}
