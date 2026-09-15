# Schema Constraints & Smithy Mappings — moved to enhanced-schemas

> **This work no longer happens in the cfn-lint repo.** As of #4539, cfn-lint
> stopped generating and patching schemas locally. The `scripts/smithy/` and
> `scripts/boto/` tooling this prompt used to describe has been removed.

## Where it lives now

Resource schemas — including Smithy-derived constraints, format keywords, and
hand-authored corrections — are produced by
[resource-provider-enhanced-schemas](https://github.com/aws-cloudformation/resource-provider-enhanced-schemas)
and published as `schemas-cfn-lint.zip` on its `latest` release. `cfn-lint
--update-specs` downloads that archive into cfn-lint's schema **cache**
(`~/.cache/aws/cfn-lint/schemas/`, or `$XDG_CACHE_HOME/aws/cfn-lint/schemas/`),
which is preferred over the package's bundled schemas when it is newer
(see `src/cfnlint/schema/manager.py`). The bundled `src/cfnlint/data/schemas/`
set is regenerated from the same source at release time.

To change a resource schema, open a PR against that repo — not this one.

## Patch layers (in the enhanced-schemas repo)

Per resource type, under `schemas/patches/extensions/<resource_type>/`:

- `manual.json` — hand-authored corrections/constraints. **Committed** (source of truth).
- `smithy.json` — generated from Smithy models. **git-ignored.**
- `format.json` — generated format keywords. **git-ignored.**

Patches apply in filename order (`format` < `manual` < `smithy`), and the
Smithy generator auto-defers to any field `manual.json` governs — so to override
a Smithy-derived constraint you add just that one field to `manual.json`.

## Typical workflow (in the enhanced-schemas checkout)

```bash
# Regenerate smithy/format patches (Smithy service-name mapping lives here now)
cfn-schemas generate

# Assemble the cfn-lint format (providers/ + resources/)
cfn-schemas assemble --output build/cfnlint

# Validate + audit patch paths
cfn-schemas validate
cfn-schemas audit-patches
```

## Validating the effect in cfn-lint (without a release)

Point cfn-lint at the freshly assembled schemas via the cache dir, then lint a
template that exercises the constraint:

```bash
# assemble produced build/cfnlint/{providers,resources}
CACHE="$XDG_CACHE_HOME/aws/cfn-lint/schemas"   # or ~/.cache/aws/cfn-lint/schemas
mkdir -p "$CACHE"
cp -r build/cfnlint/providers build/cfnlint/resources "$CACHE/"
echo '{"schema_date": "2099-01-01T00:00:00"}' > "$CACHE/version.json"  # beat the bundled date
XDG_CACHE_HOME="$XDG_CACHE_HOME" cfn-lint template.yaml
```

cfn-lint prefers the cache over its bundled schemas when the cache's
`schema_date` is newer (`ProviderSchemaManager._resolve_schema_dirs`).
