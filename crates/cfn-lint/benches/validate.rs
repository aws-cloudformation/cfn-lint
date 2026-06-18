use criterion::{black_box, criterion_group, criterion_main, Criterion};

use cfn_lint::engine::Engine;
use cfn_lint::parser;
use cfn_lint::template::Template;

fn generate_template() -> String {
    let mut yaml = String::from("AWSTemplateFormatVersion: '2010-09-09'\nResources:\n");
    for i in 0..50 {
        yaml.push_str(&format!(
            "  Bucket{i}:\n    Type: AWS::S3::Bucket\n    Properties:\n      BucketName: bucket-{i}\n",
        ));
    }
    yaml
}

fn validation_benchmarks(c: &mut Criterion) {
    let yaml = generate_template();
    let bytes = yaml.as_bytes();
    let mut group = c.benchmark_group("validation");

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

criterion_group!(benches, validation_benchmarks);
criterion_main!(benches);
