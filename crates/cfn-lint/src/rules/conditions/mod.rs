// Private (not `pub mod`) so it is not pulled into `rules::*` glob re-exports,
// which would collide with the templates anchors module of the same name.
// Anchor rules are registered via inventory regardless of module visibility.
mod anchors;
pub mod e8001;
pub mod e8002;
pub mod w8001;
