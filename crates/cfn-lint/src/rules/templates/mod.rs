// Anchor rules are consolidated here and registered via inventory; the module
// is private (not `pub mod`) so it is not pulled into `rules::*` glob
// re-exports (which would collide with the conditions anchors module).
mod anchors;
pub mod e0001;
pub mod e0100;
pub mod e0200;
pub mod e1001;
pub mod e1002;
pub mod e1003;
pub mod e1004;
pub mod e1005;
pub mod e1010;
pub mod e1011;
pub mod e1019;
pub mod e1020;
pub mod e1022;
pub mod e1029;
pub mod e1032;
pub mod e1033;
pub mod e1040;
pub mod e1041;
pub mod e1050;
pub mod i1002;
pub mod i1003;
pub mod i1022;
pub mod w1001;
pub mod w1011;
pub mod w1019;
pub mod w1020;
pub mod w1028;
pub mod w1040;
pub mod w1053;
pub mod w1054;
pub mod w1100;
