//! Validation benchmarks.
//!
//! Two families of benchmarks:
//!
//! * `synthetic/*` — the original trivial workload (many identical S3 buckets
//!   validated with a schema-less [`Engine::new`]). Cheap, stable, and useful
//!   as a floor for parse/AST-build throughput.
//! * `<fixture>/*` — realistic fixtures under `benches/fixtures/` validated with
//!   [`Engine::with_data_dir`] so schema validation, intrinsic resolution and the
//!   condition solver are actually exercised. These are the groups that catch
//!   regressions in the parts of the engine that do real work.
//!
//! `with_data_dir` gracefully falls back to rules-only mode when the schema data
//! directory has not been populated (schemas are downloaded in CI and release
//! builds), so `cargo bench` runs everywhere; the schema-validation paths are
//! measured whenever `crates/cfn-lint/data/schemas/providers` is present.

use std::path::PathBuf;

use criterion::{black_box, criterion_group, criterion_main, Criterion};

use cfn_lint::engine::Engine;
use cfn_lint::parser;
use cfn_lint::template::Template;

fn data_dir() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("data")
}

fn fixture(name: &str) -> Vec<u8> {
    let path = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .join("benches")
        .join("fixtures")
        .join(name);
    std::fs::read(&path)
        .unwrap_or_else(|e| panic!("failed to read fixture {}: {e}", path.display()))
}

/// Generate a large but trivial template: many identical S3 buckets.
fn generate_synthetic_template() -> String {
    let mut yaml = String::from("AWSTemplateFormatVersion: '2010-09-09'\nResources:\n");
    for i in 0..50 {
        yaml.push_str(&format!(
            "  Bucket{i}:\n    Type: AWS::S3::Bucket\n    Properties:\n      BucketName: bucket-{i}\n",
        ));
    }
    yaml
}

/// The original schema-less workload. Kept as a stable throughput floor.
fn synthetic_benchmarks(c: &mut Criterion) {
    let yaml = generate_synthetic_template();
    let bytes = yaml.as_bytes();
    let mut group = c.benchmark_group("synthetic");

    group.bench_function("parse", |b| {
        b.iter(|| parser::parse(black_box(bytes)).unwrap());
    });

    group.bench_function("template_from_ast", |b| {
        let ast = parser::parse(bytes).unwrap();
        b.iter(|| Template::from_ast(black_box(&ast)).unwrap());
    });

    group.bench_function("full_validate", |b| {
        let ast = parser::parse(bytes).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let regions = vec!["us-east-1".to_string()];
        b.iter(|| {
            let mut engine = Engine::new();
            engine.validate(black_box(&tmpl), black_box(&ast), &regions)
        });
    });

    group.finish();
}

/// Benchmark a realistic fixture end-to-end with schema validation enabled.
///
/// Produces three measurements per fixture:
/// * `parse` — YAML -> AST
/// * `template_from_ast` — AST -> `Template`
/// * `full_validate` — schema validation + rules + intrinsic/condition resolution
fn fixture_benchmarks(c: &mut Criterion, group_name: &str, fixture_name: &str) {
    let bytes = fixture(fixture_name);
    let regions = vec!["us-east-1".to_string()];
    let mut group = c.benchmark_group(group_name);

    group.bench_function("parse", |b| {
        b.iter(|| parser::parse(black_box(&bytes)).unwrap());
    });

    group.bench_function("template_from_ast", |b| {
        let ast = parser::parse(&bytes).unwrap();
        b.iter(|| Template::from_ast(black_box(&ast)).unwrap());
    });

    group.bench_function("full_validate", |b| {
        let ast = parser::parse(&bytes).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        b.iter(|| {
            // Rebuild the engine each iteration so the schema cache starts cold,
            // matching the CLI's per-invocation behaviour and keeping the
            // measurement comparable to `synthetic/full_validate`.
            let mut engine = Engine::with_data_dir(data_dir());
            engine.validate(black_box(&tmpl), black_box(&ast), &regions)
        });
    });

    // Also measure validation with a warm engine (schema cache reused), which
    // isolates per-template validation cost from schema-loading cost.
    group.bench_function("validate_warm_engine", |b| {
        let ast = parser::parse(&bytes).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        let mut engine = Engine::with_data_dir(data_dir());
        // Warm the schema cache once.
        let _ = engine.validate(&tmpl, &ast, &regions);
        b.iter(|| engine.validate(black_box(&tmpl), black_box(&ast), &regions));
    });

    group.finish();
}

fn conditions_benchmarks(c: &mut Criterion) {
    fixture_benchmarks(c, "conditions", "conditions.yaml");
}

fn many_resources_benchmarks(c: &mut Criterion) {
    fixture_benchmarks(c, "many_resources", "many_resources.yaml");
}

fn sam_benchmarks(c: &mut Criterion) {
    fixture_benchmarks(c, "sam", "sam.yaml");
}

criterion_group!(
    benches,
    synthetic_benchmarks,
    conditions_benchmarks,
    many_resources_benchmarks,
    sam_benchmarks,
);
criterion_main!(benches);
