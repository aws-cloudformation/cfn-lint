//! Rule registration completeness test.
//!
//! Inventory-based rule registration (`register_cfn_lint_rule!`) has no
//! compile-time guarantee that a rule file is actually wired in — a forgotten
//! `pub mod` in a `mod.rs` silently drops the rule from the registry.
//!
//! These tests pin the full set of registered rule IDs against a checked-in
//! snapshot so that any accidental drop (or duplicate) fails CI. This is what
//! proves the anchor-rule macro / registry refactors do not lose any rule.
//!
//! To regenerate the snapshot after an intentional rule addition/removal:
//!
//! ```sh
//! UPDATE_RULE_SNAPSHOT=1 cargo test -p cfn-lint --test rule_registration
//! ```

use std::collections::HashSet;

use cfn_lint::jsonschema::cfn_lint_keyword::KeywordRuleRegistry;

const SNAPSHOT_PATH: &str = concat!(env!("CARGO_MANIFEST_DIR"), "/tests/registered_rules.txt");

/// All registered rule IDs, sorted (duplicates preserved).
fn registered_rule_ids() -> Vec<String> {
    let registry = KeywordRuleRegistry::from_inventory();
    let mut ids: Vec<String> = registry
        .all_rules()
        .iter()
        .map(|rule| rule.id().to_string())
        .collect();
    ids.sort();
    ids
}

/// No two registered rules may share the same ID. A duplicate almost always
/// means a rule was registered twice (e.g. copy/paste during a refactor).
#[test]
fn test_no_duplicate_rule_ids() {
    let ids = registered_rule_ids();
    let mut seen = HashSet::new();
    let mut duplicates = Vec::new();
    for id in &ids {
        if !seen.insert(id.as_str()) {
            duplicates.push(id.clone());
        }
    }
    assert!(
        duplicates.is_empty(),
        "Duplicate rule IDs registered: {duplicates:?}"
    );
}

/// The full sorted set of registered rule IDs must match the checked-in
/// snapshot. A drop (forgotten `pub mod`) or an unexpected addition fails here.
#[test]
fn test_registered_rule_ids_match_snapshot() {
    let mut ids = registered_rule_ids();
    ids.dedup();
    let actual = format!("{}\n", ids.join("\n"));

    if std::env::var_os("UPDATE_RULE_SNAPSHOT").is_some() {
        std::fs::write(SNAPSHOT_PATH, &actual).expect("failed to write rule snapshot");
        return;
    }

    let expected = std::fs::read_to_string(SNAPSHOT_PATH).unwrap_or_else(|_| {
        panic!(
            "missing snapshot {SNAPSHOT_PATH}; regenerate with \
             UPDATE_RULE_SNAPSHOT=1 cargo test -p cfn-lint --test rule_registration"
        )
    });

    if actual.trim_end() != expected.trim_end() {
        let actual_set: HashSet<&str> = actual.lines().collect();
        let expected_set: HashSet<&str> = expected.lines().collect();
        let dropped: Vec<&str> = expected_set.difference(&actual_set).copied().collect();
        let added: Vec<&str> = actual_set.difference(&expected_set).copied().collect();
        panic!(
            "Registered rule IDs changed.\n  dropped (in snapshot, not registered): {dropped:?}\n  \
             added (registered, not in snapshot): {added:?}\n\
             If intentional, regenerate with \
             UPDATE_RULE_SNAPSHOT=1 cargo test -p cfn-lint --test rule_registration"
        );
    }
}

/// Output-rule metadata must match Python cfn-lint 1.53.1. E6002
/// (outputs/Required.py) and E6003 (outputs/Type.py) previously carried
/// transposed/leftover Export-name-uniqueness strings; this pins them.
#[test]
fn test_output_rule_metadata_parity() {
    let registry = KeywordRuleRegistry::from_inventory();
    let rules = registry.all_rules();
    let find = |id: &str| {
        rules
            .iter()
            .find(|r| r.id() == id)
            .unwrap_or_else(|| panic!("rule {id} not registered"))
    };

    let e6002 = find("E6002");
    assert_eq!(
        e6002.short_description(),
        "Outputs have required properties"
    );
    assert_eq!(
        e6002.description(),
        "Making sure the outputs have required properties"
    );

    let e6003 = find("E6003");
    assert_eq!(e6003.short_description(), "Check the type of Outputs");
    assert_eq!(
        e6003.description(),
        "Validate the type of properties in the Outputs section"
    );
}
