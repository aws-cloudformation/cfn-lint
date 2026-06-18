use crate::context::Context;
use crate::node::{AstNode, Span};
use crate::traverse;

#[derive(Debug, Clone)]
pub struct Diagnostic {
    pub span: Span,
    pub message: String,
    pub severity: Severity,
    pub rule_id: String,
}

#[derive(Debug, Clone, Copy)]
pub enum Severity {
    Error,
    Warning,
    Information,
}

/// Run built-in structural diagnostics on a Context.
/// These are fast checks that don't need schemas or external crates.
pub fn validate(ctx: &Context) -> Vec<Diagnostic> {
    let mut diags = Vec::new();
    validate_refs(ctx, &mut diags);
    validate_getatt_targets(ctx, &mut diags);
    validate_conditions(ctx, &mut diags);
    validate_findmap_targets(ctx, &mut diags);
    diags
}

/// Check that all Ref targets exist as parameters or resources.
fn validate_refs(ctx: &Context, diags: &mut Vec<Diagnostic>) {
    let pseudo_params = [
        "AWS::AccountId",
        "AWS::NotificationARNs",
        "AWS::NoValue",
        "AWS::Partition",
        "AWS::Region",
        "AWS::StackId",
        "AWS::StackName",
        "AWS::URLSuffix",
    ];

    traverse::walk(&ctx.root, &[], &mut |node, _path| {
        if let AstNode::Function(func) = node {
            if func.name == "Ref" {
                if let Some(name) = func.args.as_str() {
                    if !pseudo_params.contains(&name)
                        && !ctx.parameters.contains_key(name)
                        && !ctx.resources.contains_key(name)
                    {
                        diags.push(Diagnostic {
                            span: func.span,
                            message: format!("Ref '{}' not found in Parameters or Resources", name),
                            severity: Severity::Error,
                            rule_id: "E3012".to_string(),
                        });
                    }
                }
            }
        }
        true
    });
}

/// Check that all Fn::GetAtt targets reference existing resources.
fn validate_getatt_targets(ctx: &Context, diags: &mut Vec<Diagnostic>) {
    traverse::walk(&ctx.root, &[], &mut |node, _path| {
        if let AstNode::Function(func) = node {
            if func.name == "Fn::GetAtt" {
                let target = match func.args.as_ref() {
                    AstNode::Array(arr) => arr.elements.first().and_then(|e| e.as_str()),
                    AstNode::String(s) => s.value.split('.').next(),
                    _ => None,
                };
                if let Some(name) = target {
                    if !ctx.resources.contains_key(name) {
                        diags.push(Diagnostic {
                            span: func.span,
                            message: format!("GetAtt resource '{}' not found", name),
                            severity: Severity::Error,
                            rule_id: "E3012".to_string(),
                        });
                    }
                }
            }
        }
        true
    });
}

/// Check that all Condition references point to existing conditions.
fn validate_conditions(ctx: &Context, diags: &mut Vec<Diagnostic>) {
    traverse::walk(&ctx.root, &[], &mut |node, _path| {
        if let AstNode::Function(func) = node {
            if func.name == "Condition" {
                if let Some(name) = func.args.as_str() {
                    if !ctx.conditions.contains_key(name) {
                        diags.push(Diagnostic {
                            span: func.span,
                            message: format!("Condition '{}' not found", name),
                            severity: Severity::Error,
                            rule_id: "E8004".to_string(),
                        });
                    }
                }
            }
        }
        true
    });
}

/// Check that all FindInMap targets reference existing mappings.
fn validate_findmap_targets(ctx: &Context, diags: &mut Vec<Diagnostic>) {
    traverse::walk(&ctx.root, &[], &mut |node, _path| {
        if let AstNode::Function(func) = node {
            if func.name == "Fn::FindInMap" {
                if let Some(arr) = func.args.as_array() {
                    if let Some(name) = arr.elements.first().and_then(|e| e.as_str()) {
                        if !ctx.mappings.contains_key(name) {
                            diags.push(Diagnostic {
                                span: func.span,
                                message: format!("Mapping '{}' not found", name),
                                severity: Severity::Error,
                                rule_id: "E7002".to_string(),
                            });
                        }
                    }
                }
            }
        }
        true
    });
}
