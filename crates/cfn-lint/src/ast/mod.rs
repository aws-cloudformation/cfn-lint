pub use cfn_ast::node::*;

/// Walk the AST tree, calling `visitor` for each node with its path.
/// If `visitor` returns `false`, children of that node are skipped.
pub fn walk<F>(node: &AstNode, path: &[String], visitor: &mut F)
where
    F: FnMut(&AstNode, &[String]) -> bool,
{
    if !visitor(node, path) {
        return;
    }
    match node {
        AstNode::Object(obj) => {
            for (key, value) in obj.iter() {
                let mut child_path = path.to_vec();
                child_path.push(key.to_string());
                walk(value, &child_path, visitor);
            }
        }
        AstNode::Array(arr) => {
            for (i, elem) in arr.elements.iter().enumerate() {
                let mut child_path = path.to_vec();
                child_path.push(i.to_string());
                walk(elem, &child_path, visitor);
            }
        }
        AstNode::Function(func) => {
            walk(&func.args, path, visitor);
        }
        _ => {}
    }
}
