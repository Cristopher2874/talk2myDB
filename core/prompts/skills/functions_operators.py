FUNCTIONS_OPERATORS_SKILL = {
    "name": "functions_operators_skill",
    "description": "Provides information for functions and operators in PGQL",
    "content": """
Functions and Operators:
- Arithmetic: +, -, *, /, %, unary -
- String: || (concat)
- Relational: =, <>, <, >, <=, >=
- Logical: AND, OR, NOT
- String functions: UPPER, LOWER, SUBSTRING, LENGTH
- Numeric functions: ABS, CEIL, FLOOR, ROUND
- Datetime functions: EXTRACT(YEAR/MONTH/DAY/HOUR/MINUTE/SECOND FROM date)
- Vertex/Edge functions: VERTEX_ID, EDGE_ID, LABEL, LABELS, ID
- Predicates: IS [NOT] LABELED label, IS [NOT] SOURCE/DESTINATION OF edge
- CAST: CAST(expr AS type)
- CASE: CASE WHEN condition THEN result ... ELSE default END

Examples:
- n.age + 5
- UPPER(n.name)
- EXTRACT(YEAR FROM n.birthdate)
- CASE WHEN n.age < 18 THEN 'minor' ELSE 'adult' END
"""
}