# Verification — Trust but Verify

Never accept a claim about cfn-lint behaviour without running it. Not your own
claim, not an issue reporter's, not a PR author's. Reproduction comes first and
is cheap.

Every command below was confirmed against this repository. If one stops
working, fix this file.

## Setup, once

```shell
python -m venv .venv
.venv/bin/pip install -e ".[full]"
.venv/bin/pip install -r requirements/dev.txt
.venv/bin/cfn-lint --update-specs      # REQUIRED
```

`--update-specs` is not optional. The provider schemas are gitignored and
downloaded at runtime (see `schema-sources.md`). Without them, validation
silently falls back to the small test fixture schema set and results are
meaningless. CI runs `cfn-lint --update-specs --force` before every job.

## Running the linter

```shell
.venv/bin/cfn-lint -t template.yaml
```

### The flag gotcha that silently lints nothing

List-valued flags (`-c`, `-i`, `-r`, `-m`) consume every following argument,
including your template path:

```shell
# WRONG — the path is eaten as a rule ID, nothing is linted,
# and you get a confusing "E1001 'Resources' is a required property"
cfn-lint -c E3717 template.yaml

# RIGHT — separate the path with -t
cfn-lint -c E3717 -t template.yaml

# RIGHT — or terminate the flag list with --
cfn-lint -c E3717 -- template.yaml
```

An empty or nonsensical result from a flagged invocation almost always means
this, not a broken rule.

### `-c` adds, it does not restrict

`--include-checks` **adds** rules to the default set. It cannot narrow a run to
one rule. Confirmed: `-c E3717` on a template with an unrelated problem reports
`E3002` as well. To focus on one rule, read for its ID in the output.

Informational rules are opt-in: `-c I`.

## Running the tests

```shell
.venv/bin/python -m pytest test/unit/rules/resources/lmbd/test_function_capacity_provider_timeout.py
.venv/bin/python -m pytest test/unit/rules/            # all rule tests
```

`pyproject.toml` sets `addopts = ["-m not data"]`, so the slow data-driven
tests are deselected by default. Add `-m data` to include them.

## The full local gate, before pushing

CI runs `tox` across Python 3.10–3.15 on Linux, macOS, **and Windows**. The
style checks run as the tox `style` env, which does nothing more than
`pip install pre-commit` followed by `pre-commit run --all-files`.

`pre-commit` is **not** in `requirements/dev.txt`, so install it once:

```shell
.venv/bin/pip install pre-commit
.venv/bin/pre-commit install      # optional: run it automatically on commit
```

Then the local equivalent of CI is:

```shell
.venv/bin/python -m pytest test
.venv/bin/pre-commit run --all-files
```

`pre-commit` covers ruff, ruff-format, isort, bandit, mypy, and the JSON/YAML/
AST checks. Running it is the cheapest way to avoid a red PR.

Two recurring CI failures worth pre-empting:

- **mypy runs on all three platforms.** Platform-conditional imports
  (`fcntl` vs `msvcrt`) fail on the other OS. Add `# type: ignore[attr-defined]`
  on *both* branches; `warn_unused_ignores` is off, so this is harmless.
- **ruff-format collapses multi-line calls.** Use magic trailing commas to keep
  the formatting you intended.

## Verifying a rule actually behaves

Reproducing the bad case is half the job. The other half is proving silence.

```shell
# 1. the reported template must fail
.venv/bin/cfn-lint -t /tmp/bad.yaml

# 2. the near-miss valid template must be SILENT — this is the real test
.venv/bin/cfn-lint -t /tmp/good.yaml

# 3. no regression across the good fixtures
.venv/bin/cfn-lint -t "test/fixtures/templates/good/**/*.yaml"
```

Step 3 is the false-positive net. A new rule that lights up the good fixtures
is wrong, not the fixtures.

## Verifying an unreleased schema change

To test an enhanced-schemas change before it ships, point cfn-lint at a locally
built schema set:

```shell
XDG_CACHE_HOME=/path/to/built/cache .venv/bin/cfn-lint -t template.yaml
```

The cache must contain `providers/`, `resources/`, and a `version.json` whose
date is **newer** than the bundled one, or the local copy is ignored.

## Verifying against reality, not documentation

When a constraint's value is in question, ranked by strength:

1. **Real templates.** If templates that deploy use the value you would reject,
   the constraint is wrong. Often beats an API probe.
2. **A live API probe.** Record account, region, and date.
3. **AWS docs.** Good for intent, frequently stale on numbers.
4. **The base CFN schema.** A hint, never proof.

See `false-positives.md` for how this feeds severity and placement.
