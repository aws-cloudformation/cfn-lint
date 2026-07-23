//! C11 regression: `cli::run` must handle `BrokenPipe` gracefully.
//!
//! When cfn-lint's stdout is piped to a reader that exits early
//! (`cfn-lint --list-rules | head`), the write macros used to `unwrap()` an
//! `Err(BrokenPipe)` and panic — the native binary aborted with a backtrace
//! and, via the Python wheel, the panic surfaced as
//! "cfn-lint engine panicked: ...". Standard Unix tools instead exit quietly.
//!
//! This test spawns the built binary, then closes the read end of its stdout
//! pipe before the child begins writing (a downstream reader that exits before
//! consuming output, e.g. `cfn-lint --list-rules | head`). It asserts the
//! process was NOT killed by a signal, printed no panic/broken-pipe text to
//! stderr, and exited 0 (the would-be exit code for `--list-rules`, matching
//! Python cfn-lint).

use std::io::Read;
use std::process::{Command, Stdio};

/// Path to the `cfn-lint` binary built for this test run (provided by Cargo).
const CFN_LINT_BIN: &str = env!("CARGO_BIN_EXE_cfn-lint");

#[test]
fn list_rules_piped_to_early_closing_reader_exits_cleanly() {
    let mut child = Command::new(CFN_LINT_BIN)
        .arg("--list-rules")
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .expect("failed to spawn cfn-lint binary");

    // Capture stderr separately so we can inspect it after the process exits.
    let mut stderr = child.stderr.take().expect("child stderr");

    // Close our read end of the pipe immediately, before the child finishes its
    // startup work (arg parse, rule registry load, sort) and begins writing.
    // With no open reader, the child's first `writeln!` to stdout gets `EPIPE`
    // — a deterministic broken pipe regardless of the OS pipe buffer size (the
    // `--list-rules` output, ~16 KiB, is smaller than a typical 64 KiB pipe
    // buffer, so we cannot rely on filling it). This models a downstream reader
    // that exits before consuming output, e.g. `cfn-lint --list-rules | head`.
    drop(child.stdout.take().expect("child stdout"));

    let status = child.wait().expect("failed to wait on child");

    let mut stderr_text = String::new();
    stderr
        .read_to_string(&mut stderr_text)
        .expect("read child stderr");

    // 1. Not terminated by a signal (no SIGABRT/SIGPIPE crash).
    #[cfg(unix)]
    {
        use std::os::unix::process::ExitStatusExt;
        assert!(
            status.signal().is_none(),
            "cfn-lint was killed by signal {:?} on broken pipe; stderr:\n{}",
            status.signal(),
            stderr_text
        );
    }

    // 2. No panic / broken-pipe message leaked to stderr.
    let lower = stderr_text.to_lowercase();
    assert!(
        !lower.contains("panic"),
        "cfn-lint printed a panic message on broken pipe; stderr:\n{}",
        stderr_text
    );
    assert!(
        !lower.contains("broken pipe"),
        "cfn-lint printed a broken-pipe error on stderr; stderr:\n{}",
        stderr_text
    );

    // 3. Clean would-be exit code (0 for --list-rules, matching Python cfn-lint).
    assert_eq!(
        status.code(),
        Some(0),
        "expected exit code 0 on broken pipe, got {:?}; stderr:\n{}",
        status.code(),
        stderr_text
    );
}
