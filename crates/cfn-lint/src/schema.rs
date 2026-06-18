use std::path::PathBuf;

use thiserror::Error;

#[derive(Error, Debug)]
pub enum SchemaError {
    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),
    #[error("JSON parse error: {0}")]
    Json(#[from] serde_json::Error),
    #[error("Providers directory not found: {0}")]
    ProvidersNotFound(PathBuf),
    #[error("Update failed: {0}")]
    Update(String),
}

/// Update schemas from the CloudFormation schema endpoint.
///
/// When `force` is true, downloads all schemas from the zip archive.
/// Otherwise, incrementally updates known types via individual fetches.
#[cfg(feature = "fetch")]
pub fn update_schemas(data_dir: &std::path::Path, regions: &[String], force: bool) -> Result<(), SchemaError> {
    use cfn_schema::SchemaProvider;

    let patches_dir = data_dir.join("patches");
    let cache = cfn_schema::CacheProvider::from_dir(data_dir.to_path_buf())
        .with_patches_dir(patches_dir);
    let mut provider = cfn_schema::S3Provider::new(cache);

    if force {
        let primary = regions.first().map(|s| s.as_str()).unwrap_or("us-east-1");
        eprintln!("Downloading all schemas for {} ...", primary);
        match provider.fetch_all_from_zip(primary) {
            Ok(count) => eprintln!("Downloaded {} schemas from zip", count),
            Err(e) => return Err(SchemaError::Update(format!("Zip download failed: {}", e))),
        }
        return Ok(());
    }

    // Incremental update: fetch each known type
    let primary = regions.first().map(|s| s.as_str()).unwrap_or("us-east-1");
    let known_types = provider.resource_types(primary);

    if known_types.is_empty() {
        return Err(SchemaError::Update(
            "No known resource types. Use --force for initial download.".into(),
        ));
    }

    let mut updated = 0;
    let mut errors = 0;
    let total = known_types.len() * regions.len();

    for region in regions {
        for type_name in &known_types {
            match provider.fetch_type(type_name, region) {
                Ok(true) => updated += 1,
                Ok(false) => {}
                Err(e) => {
                    eprintln!("  Warning: failed to fetch {} in {}: {}", type_name, region, e);
                    errors += 1;
                }
            }
        }
    }

    eprintln!("Updated {}/{} schemas ({} errors)", updated, total, errors);
    Ok(())
}

#[cfg(not(feature = "fetch"))]
pub fn update_schemas(_data_dir: &std::path::Path, _regions: &[String], _force: bool) -> Result<(), SchemaError> {
    Err(SchemaError::Update(
        "Schema fetching not available. Build with --features fetch".into(),
    ))
}
