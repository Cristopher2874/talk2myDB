SYNTAX_RULES_SKILL = {
    "name": "syntax_rules_skill",
    "description": "Provides information for syntactic rules in PGQL",
    "content": """
Syntactic Rules:
- Identifiers: Unquoted (auto-uppercase), Quoted "with spaces"
- Literals: 'strings', 123, 12.34, true/false, DATE '2023-01-01', TIME '12:00:00'
- Comments: /* comment */
- Keywords: SELECT, FROM, MATCH, WHERE, etc. (case-insensitive)
- Bind variables: ? for parameterized queries
- Property access: variable.property_name
- Label access: variable IS label

Examples:
- Property: n.first_name
- Label: n IS Person
- Quoted identifier: n."first name"
- Bind variable: WHERE n.age > ?
"""
}