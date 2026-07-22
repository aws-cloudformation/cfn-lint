use std::process;

fn main() {
    // All CLI logic lives in `cfn_lint::cli::run`, which returns an exit code
    // instead of calling `process::exit` directly. This keeps the exact same
    // implementation shared with the Python bindings' `cli_main` entry point.
    process::exit(cfn_lint::cli::run(std::env::args_os()));
}
