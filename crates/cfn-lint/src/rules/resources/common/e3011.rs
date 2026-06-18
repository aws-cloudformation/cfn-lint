use crate::ast::AstNode;
use crate::rules::Severity;
use crate::jsonschema::ValidationError;
use crate::template::Template;
use crate::jsonschema::cfn_lint_keyword::CfnLintRule;

/// E3011: Check property names in Resources.
///
/// Mirrors Python cfn-lint `resources/PropertyNames.py`. Resource logical IDs
/// must not exceed 255 characters (CloudFormation limit).
pub struct E3011;

impl CfnLintRule for E3011 {
    fn id(&self) -> &str {
        "E3011"
    }

    fn short_description(&self) -> &str {
        "Check property names in Resources"
    }

    fn description(&self) -> &str {
        "Validate property names are properly configured in Resources"
    }

    fn severity(&self) -> Severity {
        Severity::Error
    }

    fn keywords(&self) -> &[&str] {
        &["/"]
    }

    fn validate_template(&self, _template: &Template, _root: &AstNode) -> Vec<crate::jsonschema::ValidationError> {
        // Validation is handled by the schema pipeline's propertyNames keyword (maps to "E3011")
                vec![]
    }
}

crate::register_cfn_lint_rule!(E3011);

#[cfg(test)]
mod tests {
    use super::*;
    use crate::parser;

    #[test]
    fn test_validate_is_stub() {
        // Validation is handled by the schema pipeline's propertyNames keyword;
        // this rule struct is only a metadata holder for the rule registry.
        let long_name = "A".repeat(256);
        let yaml = format!(
            "Resources:\n  {}:\n    Type: AWS::S3::Bucket\n",
            long_name
        );
        let ast = parser::parse(yaml.as_bytes()).unwrap();
        let tmpl = Template::from_ast(&ast).unwrap();
        assert!(E3011.validate_template(&tmpl, &ast).is_empty());
    }
}
