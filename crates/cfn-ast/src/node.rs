use std::fmt;

#[derive(Debug, Clone, Copy, PartialEq, Eq, Default)]
pub struct Position {
    pub line: u32,
    pub column: u32,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Default)]
pub struct Span {
    pub start: Position,
    pub end: Position,
}

#[derive(Debug, Clone)]
pub enum AstNode {
    Object(ObjectNode),
    Array(ArrayNode),
    String(StringNode),
    Number(NumberNode),
    Bool(BoolNode),
    Null(NullNode),
    Function(FunctionNode),
}

/// A single key-value entry in an object node.
#[derive(Debug, Clone)]
pub struct ObjectEntry {
    /// The original key node (preserves type: string, number, bool, function, etc.)
    pub key_node: AstNode,
    /// Convenience stringified key for lookups.
    pub key: String,
    /// The value node.
    pub value: AstNode,
    /// Span of the key in source.
    pub key_span: Span,
}

#[derive(Debug, Clone)]
pub struct ObjectNode {
    /// Ordered list of entries, preserving duplicates and non-string keys.
    pub entries: Vec<ObjectEntry>,
    pub span: Span,
}

impl ObjectNode {
    /// Get the first value for a key (most common access pattern).
    pub fn get(&self, key: &str) -> Option<&AstNode> {
        self.entries.iter().find(|e| e.key == key).map(|e| &e.value)
    }

    /// Check if any entry has this key.
    pub fn contains_key(&self, key: &str) -> bool {
        self.entries.iter().any(|e| e.key == key)
    }

    /// Iterate over all (key, value) pairs including duplicates.
    pub fn iter(&self) -> impl Iterator<Item = (&str, &AstNode)> {
        self.entries.iter().map(|e| (e.key.as_str(), &e.value))
    }

    /// Iterate over all keys in order (may contain duplicates).
    pub fn keys(&self) -> impl Iterator<Item = &str> {
        self.entries.iter().map(|e| e.key.as_str())
    }

    /// Iterate over values in order.
    pub fn values(&self) -> impl Iterator<Item = &AstNode> {
        self.entries.iter().map(|e| &e.value)
    }

    /// Number of entries (including duplicates).
    pub fn len(&self) -> usize {
        self.entries.len()
    }

    pub fn is_empty(&self) -> bool {
        self.entries.is_empty()
    }

    /// Get the key span for a given key name.
    pub fn key_span(&self, key: &str) -> Option<Span> {
        self.entries.iter().find(|e| e.key == key).map(|e| e.key_span)
    }

    /// Check if a key was originally a non-string node.
    pub fn is_non_string_key(&self, key: &str) -> bool {
        self.entries.iter().any(|e| e.key == key && !matches!(e.key_node, AstNode::String(_)))
    }

    /// Get all entries with duplicate keys.
    pub fn duplicate_keys(&self) -> Vec<&ObjectEntry> {
        let mut seen = std::collections::HashSet::new();
        let mut dupes = Vec::new();
        for entry in &self.entries {
            if !seen.insert(&entry.key) {
                dupes.push(entry);
            }
        }
        dupes
    }

    /// Get all entries with non-string keys.
    pub fn non_string_key_entries(&self) -> Vec<&ObjectEntry> {
        self.entries.iter().filter(|e| !matches!(e.key_node, AstNode::String(_))).collect()
    }
}

#[derive(Debug, Clone)]
pub struct ArrayNode {
    pub elements: Vec<AstNode>,
    pub span: Span,
}

#[derive(Debug, Clone)]
pub struct StringNode {
    pub value: String,
    pub span: Span,
}

#[derive(Debug, Clone)]
pub struct NumberNode {
    pub value: f64,
    pub span: Span,
}

#[derive(Debug, Clone)]
pub struct BoolNode {
    pub value: bool,
    pub span: Span,
}

#[derive(Debug, Clone)]
pub struct NullNode {
    pub span: Span,
}

#[derive(Debug, Clone)]
pub struct FunctionNode {
    pub name: String,
    pub args: Box<AstNode>,
    pub span: Span,
}

impl AstNode {
    pub fn span(&self) -> Span {
        match self {
            AstNode::Object(n) => n.span,
            AstNode::Array(n) => n.span,
            AstNode::String(n) => n.span,
            AstNode::Number(n) => n.span,
            AstNode::Bool(n) => n.span,
            AstNode::Null(n) => n.span,
            AstNode::Function(n) => n.span,
        }
    }

    pub fn get(&self, key: &str) -> Option<&AstNode> {
        match self {
            AstNode::Object(obj) => obj.get(key),
            _ => None,
        }
    }

    pub fn as_str(&self) -> Option<&str> {
        match self {
            AstNode::String(s) => Some(&s.value),
            _ => None,
        }
    }

    pub fn as_f64(&self) -> Option<f64> {
        match self {
            AstNode::Number(n) => Some(n.value),
            _ => None,
        }
    }

    pub fn as_bool(&self) -> Option<bool> {
        match self {
            AstNode::Bool(b) => Some(b.value),
            _ => None,
        }
    }

    pub fn as_object(&self) -> Option<&ObjectNode> {
        match self {
            AstNode::Object(o) => Some(o),
            _ => None,
        }
    }

    pub fn as_object_mut(&mut self) -> Option<&mut ObjectNode> {
        match self {
            AstNode::Object(o) => Some(o),
            _ => None,
        }
    }

    pub fn as_array(&self) -> Option<&ArrayNode> {
        match self {
            AstNode::Array(a) => Some(a),
            _ => None,
        }
    }

    pub fn as_function(&self) -> Option<&FunctionNode> {
        match self {
            AstNode::Function(f) => Some(f),
            _ => None,
        }
    }

    pub fn is_null(&self) -> bool {
        matches!(self, AstNode::Null(_))
    }

    pub fn node_type(&self) -> &str {
        match self {
            AstNode::Object(_) => "object",
            AstNode::Array(_) => "array",
            AstNode::String(_) => "string",
            AstNode::Number(n) => {
                if n.value.fract() == 0.0 { "integer" } else { "number" }
            }
            AstNode::Bool(_) => "boolean",
            AstNode::Null(_) => "null",
            AstNode::Function(_) => "function",
        }
    }
}

impl fmt::Display for AstNode {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            AstNode::String(s) => write!(f, "\"{}\"", s.value),
            AstNode::Number(n) => write!(f, "{}", n.value),
            AstNode::Bool(b) => write!(f, "{}", b.value),
            AstNode::Null(_) => write!(f, "null"),
            AstNode::Object(_) => write!(f, "{{...}}"),
            AstNode::Array(_) => write!(f, "[...]"),
            AstNode::Function(func) => write!(f, "{}(...)", func.name),
        }
    }
}
