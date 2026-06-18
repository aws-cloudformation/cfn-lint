//! Function resolvers for CloudFormation intrinsic functions.
//!
//! Mirrors Python's `cfnlint.jsonschema._resolvers_cfn`.
//! Each resolver takes a function's arguments and yields
//! `(resolved_value, context)` pairs representing all possible
//! resolved values with their evolved contexts.

use std::sync::LazyLock;

use regex::Regex;

use crate::ast::{AstNode, ArrayNode, Span, StringNode};
use crate::context::Context;

static RE_SUB_VARS: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"\$\{([^!].*?)\}").unwrap());

/// A resolved value with its evolved context.
pub struct Resolved {
    pub value: AstNode,
    pub context: Context,
}

/// Resolve an AstNode to all possible concrete values.
/// Non-function nodes yield themselves. Functions dispatch to their resolver.
pub fn resolve_value(ctx: &Context, node: &AstNode) -> Vec<Resolved> {
    if let Some(func) = node.as_function() {
        match func.name.as_str() {
            "Ref" => resolve_ref(ctx, &func.args),
            "Fn::If" => resolve_if(ctx, &func.args),
            "Fn::GetAZs" => resolve_getazs(ctx, &func.args),
            "Fn::Join" => resolve_join(ctx, &func.args),
            "Fn::Select" => resolve_select(ctx, &func.args),
            "Fn::Split" => resolve_split(ctx, &func.args),
            "Fn::Sub" => resolve_sub(ctx, &func.args),
            "Fn::FindInMap" => resolve_find_in_map(ctx, &func.args),
            // Fn::Base64 is a passthrough — resolve its argument
            "Fn::Base64" => resolve_value(ctx, &func.args),
            // Unresolvable functions
            _ => vec![],
        }
    } else {
        vec![Resolved {
            value: node.clone(),
            context: ctx.clone(),
        }]
    }
}

/// Ref resolver: resolve parameter/pseudo-parameter references.
fn resolve_ref(ctx: &Context, args: &AstNode) -> Vec<Resolved> {
    let name = match args.as_str() {
        Some(s) => s,
        None => return vec![],
    };
    ctx.resolve_ref(name)
        .into_iter()
        .map(|s| Resolved {
            value: s.value,
            context: s.context,
        })
        .collect()
}

/// Fn::If resolver: branch into true/false with evolved condition state.
fn resolve_if(ctx: &Context, args: &AstNode) -> Vec<Resolved> {
    let arr = match args.as_array() {
        Some(a) if a.elements.len() == 3 => a,
        _ => return vec![],
    };
    let condition = match arr.elements[0].as_str() {
        Some(s) => s.to_string(),
        None => return vec![],
    };

    let mut results = Vec::new();

    // True branch — only explore if not pinned false AND SAT-satisfiable
    if ctx.condition_state.get(&condition) != Some(&false)
        && ctx.is_condition_satisfiable(&condition, true)
    {
        let mut true_ctx = ctx.clone();
        true_ctx.condition_state.insert(condition.clone(), true);
        results.extend(resolve_value(&true_ctx, &arr.elements[1]));
    }

    // False branch — only explore if not pinned true AND SAT-satisfiable
    if ctx.condition_state.get(&condition) != Some(&true)
        && ctx.is_condition_satisfiable(&condition, false)
    {
        let mut false_ctx = ctx.clone();
        false_ctx.condition_state.insert(condition, false);
        results.extend(resolve_value(&false_ctx, &arr.elements[2]));
    }

    results
}

/// Fn::GetAZs resolver: resolve to list of AZ strings for the region.
fn resolve_getazs(ctx: &Context, args: &AstNode) -> Vec<Resolved> {
    // First resolve the argument (could be Ref, empty string, or region name)
    let resolved_args = resolve_value(ctx, args);
    let mut results = Vec::new();

    for r in resolved_args {
        let region_str = match r.value.as_str() {
            Some(s) => s.to_string(),
            None => continue,
        };

        if region_str.is_empty() {
            // Empty string means current region
            for region in &r.context.regions {
                if let Some(azs) = get_azs_for_region(region) {
                    results.push(Resolved {
                        value: azs_to_ast(&azs),
                        context: r.context.clone(),
                    });
                }
            }
        } else if let Some(azs) = get_azs_for_region(&region_str) {
            results.push(Resolved {
                value: azs_to_ast(&azs),
                context: r.context.clone(),
            });
        }
    }

    results
}

/// Fn::Join resolver.
fn resolve_join(ctx: &Context, args: &AstNode) -> Vec<Resolved> {
    let arr = match args.as_array() {
        Some(a) if a.elements.len() == 2 => a,
        _ => return vec![],
    };

    let mut results = Vec::new();
    for delim_r in resolve_value(ctx, &arr.elements[0]) {
        let delim = match delim_r.value.as_str() {
            Some(s) => s.to_string(),
            None => continue,
        };
        for list_r in resolve_value(&delim_r.context, &arr.elements[1]) {
            let items = match list_r.value.as_array() {
                Some(a) => a,
                None => continue,
            };
            // Try to resolve all items to strings
            if let Some(strings) = resolve_array_to_strings(&list_r.context, &items.elements) {
                for combo in strings {
                    results.push(Resolved {
                        value: str_node(&combo.values.join(&delim)),
                        context: combo.context,
                    });
                }
            }
        }
    }
    results
}

/// Fn::Select resolver.
fn resolve_select(ctx: &Context, args: &AstNode) -> Vec<Resolved> {
    let arr = match args.as_array() {
        Some(a) if a.elements.len() == 2 => a,
        _ => return vec![],
    };

    let mut results = Vec::new();
    for idx_r in resolve_value(ctx, &arr.elements[0]) {
        let idx = match to_usize(&idx_r.value) {
            Some(i) => i,
            None => continue,
        };
        for list_r in resolve_value(&idx_r.context, &arr.elements[1]) {
            let items = match list_r.value.as_array() {
                Some(a) => a,
                None => continue,
            };
            if idx < items.elements.len() {
                results.extend(resolve_value(&list_r.context, &items.elements[idx]));
            }
        }
    }
    results
}

/// Fn::Split resolver.
fn resolve_split(ctx: &Context, args: &AstNode) -> Vec<Resolved> {
    let arr = match args.as_array() {
        Some(a) if a.elements.len() == 2 => a,
        _ => return vec![],
    };

    let mut results = Vec::new();
    for delim_r in resolve_value(ctx, &arr.elements[0]) {
        let delim = match delim_r.value.as_str() {
            Some(s) => s.to_string(),
            None => continue,
        };
        for src_r in resolve_value(&delim_r.context, &arr.elements[1]) {
            let src = match src_r.value.as_str() {
                Some(s) => s.to_string(),
                None => continue,
            };
            let parts: Vec<AstNode> = src.split(&delim).map(|s| str_node(s)).collect();
            results.push(Resolved {
                value: AstNode::Array(ArrayNode {
                    elements: parts,
                    span: Span::default(),
                }),
                context: src_r.context,
            });
        }
    }
    results
}

/// Fn::Sub resolver.
fn resolve_sub(ctx: &Context, args: &AstNode) -> Vec<Resolved> {
    let (template_str, extra_ctx) = match args {
        AstNode::String(s) => (s.value.clone(), None),
        _ => {
            if let Some(arr) = args.as_array() {
                if arr.elements.len() == 2 {
                    let s = match arr.elements[0].as_str() {
                        Some(s) => s.to_string(),
                        None => return vec![],
                    };
                    Some((s, Some(&arr.elements[1])))
                } else {
                    None
                }
            } else {
                None
            }
            .unwrap_or_else(|| return (String::new(), None))
        }
    };

    if template_str.is_empty() {
        return vec![Resolved {
            value: AstNode::String(crate::ast::StringNode {
                value: String::new(),
                span: crate::ast::Span::default(),
            }),
            context: ctx.clone(),
        }];
    }

    // Build ref_values from the extra map if provided
    let mut base_ctx = ctx.clone();
    if let Some(map_node) = extra_ctx {
        if let Some(obj) = map_node.as_object() {
            for (key, val) in obj.iter() {
                let resolved = resolve_value(&base_ctx, val);
                if let Some(first) = resolved.into_iter().next() {
                    // Take evolved condition_state from resolving the value,
                    // but preserve our accumulated ref_values.
                    base_ctx.condition_state = first.context.condition_state;
                    base_ctx.ref_values.insert(key.to_string(), first.value);
                }
            }
        }
    }

    // Find ${VarName} patterns and substitute using single-pass replacement
    // to avoid corruption when replacement values contain ${...} patterns.
    let mut final_ctx = base_ctx.clone();
    let mut failed = false;

    // Collect match positions and variable names first
    let matches: Vec<(usize, usize, String)> = RE_SUB_VARS
        .captures_iter(&template_str)
        .map(|cap| {
            let m = cap.get(0).unwrap();
            (m.start(), m.end(), cap[1].trim().to_string())
        })
        .collect();

    // Build result in a single pass from left to right
    let mut result = String::with_capacity(template_str.len());
    let mut last_end = 0;

    for (start, end, var_name) in &matches {
        result.push_str(&template_str[last_end..*start]);

        // Try ref_values first, then resolve as Ref
        if let Some(val) = final_ctx.ref_values.get(var_name) {
            if let Some(s) = val.as_str() {
                result.push_str(s);
                last_end = *end;
                continue;
            }
        }
        // Try resolving as a Ref
        let scenarios = final_ctx.resolve_ref(var_name);
        if let Some(first) = scenarios.into_iter().next() {
            if let Some(s) = first.value.as_str() {
                result.push_str(s);
                final_ctx = first.context;
                last_end = *end;
                continue;
            }
        }
        // Can't resolve this variable
        failed = true;
        break;
    }

    if failed {
        return vec![];
    }

    // Append any remaining text after the last match
    result.push_str(&template_str[last_end..]);

    vec![Resolved {
        value: str_node(&result),
        context: final_ctx,
    }]
}

/// Fn::FindInMap resolver.
fn resolve_find_in_map(ctx: &Context, args: &AstNode) -> Vec<Resolved> {
    let arr = match args.as_array() {
        Some(a) if a.elements.len() >= 3 => a,
        _ => return vec![],
    };

    let mut results = Vec::new();
    for map_r in resolve_value(ctx, &arr.elements[0]) {
        let map_name = match map_r.value.as_str() {
            Some(s) => s.to_string(),
            None => continue,
        };
        for key1_r in resolve_value(&map_r.context, &arr.elements[1]) {
            let key1 = match key1_r.value.as_str() {
                Some(s) => s.to_string(),
                None => continue,
            };
            for key2_r in resolve_value(&key1_r.context, &arr.elements[2]) {
                let key2 = match key2_r.value.as_str() {
                    Some(s) => s.to_string(),
                    None => continue,
                };
                // Look up in template mappings
                if let Some(val) = key2_r
                    .context
                    .template
                    .mappings
                    .get(&map_name)
                    .and_then(|m| m.get(&key1))
                    .and_then(|m| m.get(&key2))
                {
                    results.push(Resolved {
                        value: val.clone(),
                        context: key2_r.context.clone(),
                    });
                }
            }
        }
    }
    results
}

// ── Helpers ──

fn str_node(s: &str) -> AstNode {
    AstNode::String(StringNode {
        value: s.to_string(),
        span: Span::default(),
    })
}

fn to_usize(node: &AstNode) -> Option<usize> {
    if let Some(s) = node.as_str() {
        s.parse().ok()
    } else if let Some(n) = node.as_f64() {
        if n < 0.0 { return None; }
        Some(n as usize)
    } else {
        None
    }
}

struct StringCombo {
    values: Vec<String>,
    context: Context,
}

fn resolve_array_to_strings(ctx: &Context, items: &[AstNode]) -> Option<Vec<StringCombo>> {
    if items.is_empty() {
        return Some(vec![StringCombo {
            values: vec![],
            context: ctx.clone(),
        }]);
    }

    let mut combos = vec![StringCombo {
        values: vec![],
        context: ctx.clone(),
    }];

    const MAX_COMBOS: usize = 128;

    for item in items {
        let mut new_combos = Vec::new();
        for combo in &combos {
            let resolved = resolve_value(&combo.context, item);
            if resolved.is_empty() {
                return None;
            }
            for r in resolved {
                let s = match r.value.as_str() {
                    Some(s) => s.to_string(),
                    None => match r.value.as_f64() {
                        Some(n) => n.to_string(),
                        None => return None,
                    },
                };
                let mut new_vals = combo.values.clone();
                new_vals.push(s);
                new_combos.push(StringCombo {
                    values: new_vals,
                    context: r.context,
                });
                if new_combos.len() > MAX_COMBOS {
                    return None;
                }
            }
        }
        combos = new_combos;
    }

    Some(combos)
}

/// Get availability zones for a region.
fn get_azs_for_region(region: &str) -> Option<Vec<String>> {
    // Hardcoded AZ data matching Python's AVAILABILITY_ZONES
    let azs: &[&str] = match region {
        "af-south-1" => &["af-south-1a", "af-south-1b", "af-south-1c"],
        "ap-east-1" => &["ap-east-1a", "ap-east-1b", "ap-east-1c"],
        "ap-northeast-1" => &["ap-northeast-1a", "ap-northeast-1b", "ap-northeast-1c", "ap-northeast-1d"],
        "ap-northeast-2" => &["ap-northeast-2a", "ap-northeast-2b", "ap-northeast-2c", "ap-northeast-2d"],
        "ap-northeast-3" => &["ap-northeast-3a", "ap-northeast-3b", "ap-northeast-3c"],
        "ap-south-1" => &["ap-south-1a", "ap-south-1b", "ap-south-1c"],
        "ap-south-2" => &["ap-south-2a", "ap-south-2b", "ap-south-2c"],
        "ap-southeast-1" => &["ap-southeast-1a", "ap-southeast-1b", "ap-southeast-1c"],
        "ap-southeast-2" => &["ap-southeast-2a", "ap-southeast-2b", "ap-southeast-2c"],
        "ap-southeast-3" => &["ap-southeast-3a", "ap-southeast-3b", "ap-southeast-3c"],
        "ap-southeast-4" => &["ap-southeast-4a", "ap-southeast-4b", "ap-southeast-4c"],
        "ca-central-1" => &["ca-central-1a", "ca-central-1b", "ca-central-1d"],
        "ca-west-1" => &["ca-west-1a", "ca-west-1b", "ca-west-1c"],
        "cn-north-1" => &["cn-north-1a", "cn-north-1b", "cn-north-1c"],
        "cn-northwest-1" => &["cn-northwest-1a", "cn-northwest-1b", "cn-northwest-1c"],
        "eu-central-1" => &["eu-central-1a", "eu-central-1b", "eu-central-1c"],
        "eu-central-2" => &["eu-central-2a", "eu-central-2b", "eu-central-2c"],
        "eu-north-1" => &["eu-north-1a", "eu-north-1b", "eu-north-1c"],
        "eu-south-1" => &["eu-south-1a", "eu-south-1b", "eu-south-1c"],
        "eu-south-2" => &["eu-south-2a", "eu-south-2b", "eu-south-2c"],
        "eu-west-1" => &["eu-west-1a", "eu-west-1b", "eu-west-1c"],
        "eu-west-2" => &["eu-west-2a", "eu-west-2b", "eu-west-2c"],
        "eu-west-3" => &["eu-west-3a", "eu-west-3b", "eu-west-3c"],
        "il-central-1" => &["il-central-1a", "il-central-1b", "il-central-1c"],
        "me-central-1" => &["me-central-1a", "me-central-1b", "me-central-1c"],
        "me-south-1" => &["me-south-1a", "me-south-1b", "me-south-1c"],
        "sa-east-1" => &["sa-east-1a", "sa-east-1b", "sa-east-1c"],
        "us-east-1" => &["us-east-1a", "us-east-1b", "us-east-1c", "us-east-1d", "us-east-1e", "us-east-1f"],
        "us-east-2" => &["us-east-2a", "us-east-2b", "us-east-2c"],
        "us-gov-east-1" => &["us-gov-east-1a", "us-gov-east-1b", "us-gov-east-1c"],
        "us-gov-west-1" => &["us-gov-west-1a", "us-gov-west-1b", "us-gov-west-1c"],
        "us-west-1" => &["us-west-1a", "us-west-1b"],
        "us-west-2" => &["us-west-2a", "us-west-2b", "us-west-2c", "us-west-2d"],
        _ => return None,
    };
    Some(azs.iter().map(|s| s.to_string()).collect())
}

fn azs_to_ast(azs: &[String]) -> AstNode {
    AstNode::Array(ArrayNode {
        elements: azs.iter().map(|s| str_node(s)).collect(),
        span: Span::default(),
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;
    use crate::template::Template;
    use std::sync::Arc;

    fn ctx_from(yaml: &[u8]) -> (AstNode, Context) {
        let ast = parser::parse(yaml).unwrap();
        let tmpl = Arc::new(Template::from_ast(&ast).unwrap());
        (ast, Context::new(tmpl))
    }

    #[test]
    fn test_resolve_literal() {
        let node = str_node("hello");
        let (_, ctx) = ctx_from(b"AWSTemplateFormatVersion: '2010-09-09'\n");
        let results = resolve_value(&ctx, &node);
        assert_eq!(results.len(), 1);
        assert_eq!(results[0].value.as_str(), Some("hello"));
    }

    #[test]
    fn test_resolve_ref_pseudo() {
        let (ast, ctx) = ctx_from(b"val: !Ref 'AWS::Region'\n");
        let val = ast.get("val").unwrap();
        let results = resolve_value(&ctx, val);
        assert_eq!(results.len(), 1);
        assert_eq!(results[0].value.as_str(), Some("us-east-1"));
    }

    #[test]
    fn test_resolve_ref_param_allowed_values() {
        let (ast, ctx) = ctx_from(
            b"Parameters:\n  Env:\n    Type: String\n    AllowedValues:\n      - dev\n      - prod\nResources:\n  D:\n    Type: AWS::SNS::Topic\nval: !Ref Env\n",
        );
        let val = ast.get("val").unwrap();
        let results = resolve_value(&ctx, val);
        assert_eq!(results.len(), 2);
        let vals: Vec<_> = results.iter().filter_map(|r| r.value.as_str()).collect();
        assert!(vals.contains(&"dev"));
        assert!(vals.contains(&"prod"));
    }

    #[test]
    fn test_resolve_if() {
        let (ast, ctx) = ctx_from(
            b"val:\n  Fn::If:\n    - IsProd\n    - prod\n    - dev\n",
        );
        let val = ast.get("val").unwrap();
        let results = resolve_value(&ctx, val);
        assert_eq!(results.len(), 2);
        let vals: Vec<_> = results.iter().filter_map(|r| r.value.as_str()).collect();
        assert!(vals.contains(&"prod"));
        assert!(vals.contains(&"dev"));
    }

    #[test]
    fn test_resolve_getazs_empty_string() {
        let (ast, ctx) = ctx_from(b"val:\n  Fn::GetAZs: ''\n");
        let val = ast.get("val").unwrap();
        let results = resolve_value(&ctx, val);
        assert_eq!(results.len(), 1);
        let arr = results[0].value.as_array().unwrap();
        assert_eq!(arr.elements[0].as_str(), Some("us-east-1a"));
    }

    #[test]
    fn test_resolve_getazs_region() {
        let (ast, ctx) = ctx_from(b"val:\n  Fn::GetAZs: us-west-2\n");
        let val = ast.get("val").unwrap();
        let results = resolve_value(&ctx, val);
        assert_eq!(results.len(), 1);
        let arr = results[0].value.as_array().unwrap();
        assert_eq!(arr.elements.len(), 4);
        assert_eq!(arr.elements[0].as_str(), Some("us-west-2a"));
    }

    #[test]
    fn test_resolve_getazs_ref_region() {
        let (ast, ctx) = ctx_from(b"val:\n  Fn::GetAZs: !Ref 'AWS::Region'\n");
        let val = ast.get("val").unwrap();
        let results = resolve_value(&ctx, val);
        assert_eq!(results.len(), 1);
        let arr = results[0].value.as_array().unwrap();
        assert_eq!(arr.elements[0].as_str(), Some("us-east-1a"));
    }

    #[test]
    fn test_resolve_join() {
        let (ast, ctx) = ctx_from(b"val:\n  Fn::Join:\n    - '-'\n    - - a\n      - b\n      - c\n");
        let val = ast.get("val").unwrap();
        let results = resolve_value(&ctx, val);
        assert_eq!(results.len(), 1);
        assert_eq!(results[0].value.as_str(), Some("a-b-c"));
    }

    #[test]
    fn test_resolve_select() {
        let (ast, ctx) = ctx_from(b"val:\n  Fn::Select:\n    - 1\n    - - a\n      - b\n      - c\n");
        let val = ast.get("val").unwrap();
        let results = resolve_value(&ctx, val);
        assert_eq!(results.len(), 1);
        assert_eq!(results[0].value.as_str(), Some("b"));
    }

    #[test]
    fn test_resolve_split() {
        let (ast, ctx) = ctx_from(b"val:\n  Fn::Split:\n    - ','\n    - 'a,b,c'\n");
        let val = ast.get("val").unwrap();
        let results = resolve_value(&ctx, val);
        assert_eq!(results.len(), 1);
        let arr = results[0].value.as_array().unwrap();
        assert_eq!(arr.elements.len(), 3);
        assert_eq!(arr.elements[1].as_str(), Some("b"));
    }

    #[test]
    fn test_resolve_sub_simple() {
        let (ast, ctx) = ctx_from(
            b"val:\n  Fn::Sub: 'arn:aws:s3:::${AWS::Region}-bucket'\n",
        );
        let val = ast.get("val").unwrap();
        let results = resolve_value(&ctx, val);
        assert_eq!(results.len(), 1);
        assert_eq!(
            results[0].value.as_str(),
            Some("arn:aws:s3:::us-east-1-bucket")
        );
    }

    #[test]
    fn test_resolve_find_in_map() {
        let (ast, ctx) = ctx_from(
            b"Mappings:\n  RegionMap:\n    us-east-1:\n      AMI: ami-12345\nResources:\n  D:\n    Type: AWS::SNS::Topic\nval:\n  Fn::FindInMap:\n    - RegionMap\n    - us-east-1\n    - AMI\n",
        );
        let val = ast.get("val").unwrap();
        let results = resolve_value(&ctx, val);
        assert_eq!(results.len(), 1);
        assert_eq!(results[0].value.as_str(), Some("ami-12345"));
    }

    #[test]
    fn test_resolve_nested_ref_in_sub() {
        let (ast, ctx) = ctx_from(
            b"Parameters:\n  Env:\n    Type: String\n    Default: prod\nResources:\n  D:\n    Type: AWS::SNS::Topic\nval:\n  Fn::Sub: '${Env}-app'\n",
        );
        let val = ast.get("val").unwrap();
        let results = resolve_value(&ctx, val);
        assert_eq!(results.len(), 1);
        assert_eq!(results[0].value.as_str(), Some("prod-app"));
    }
}
