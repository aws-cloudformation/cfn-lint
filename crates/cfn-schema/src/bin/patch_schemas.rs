//! Apply JSON patches to all resource schemas on disk.
//!
//! Usage: patch-schemas <schemas-dir> <patches-dir>
//!
//! Reads type→hash mappings from `<schemas-dir>/providers/*.json`,
//! applies patches from `<patches-dir>`, and writes patched schemas
//! back to `<schemas-dir>/resources/`.

use std::collections::{HashMap, HashSet};
use std::path::PathBuf;

fn main() {
    let args: Vec<String> = std::env::args().collect();
    if args.len() != 3 {
        eprintln!("Usage: patch-schemas <schemas-dir> <patches-dir>");
        eprintln!("  e.g. patch-schemas crates/cfn-lint/data/schemas crates/cfn-schema/data/patches");
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
        let content = match std::fs::read_to_string(&schema_path) {
            Ok(c) => c,
            Err(_) => continue,
        };
        let mut schema: serde_json::Value = match serde_json::from_str(&content) {
            Ok(v) => v,
            Err(_) => continue,
        };

        let before = schema.to_string();
        let mut sorted_types: Vec<_> = types.iter().collect();
        sorted_types.sort();
        for rtype in sorted_types {
            cfn_schema::patch::apply_patches_for_type(&mut schema, &patches_dir, rtype);
        }

        if schema.to_string() != before {
            let out = serde_json::to_string_pretty(&schema).unwrap();
            std::fs::write(&schema_path, out.as_bytes()).unwrap();
            patched_count += 1;
        }
    }

    eprintln!("Patched {} schemas", patched_count);
}
