BASIC_QUERY_STRUCTURE = """
PGQL Query Structure:
- SELECT clause: Defines columns to return
  - SELECT DISTINCT? expression (AS alias)?, ...
  - SELECT * for all visible variables
- FROM clause: Defines graph pattern to match
  - GRAPH_TABLE(graph_name MATCH pattern COLUMNS(...))
- WHERE clause: Filters results
  - Boolean expressions with property references, comparisons
- GROUP BY: Groups results for aggregation
- ORDER BY: Sorts results
- LIMIT/OFFSET: Limits and offsets results

Example:
SELECT n.name, COUNT(e) AS degree
FROM GRAPH_TABLE(my_graph MATCH (n) -[e]-> () COLUMNS(n.name))
GROUP BY n.name
ORDER BY degree DESC
"""

GRAPH_PATTERNS = """
Graph Pattern Matching:
- Vertex patterns: (variable IS? label)
- Edge patterns: -[variable IS? label]-> (outgoing), <-[variable IS? label]- (incoming), -[variable IS? label]- (any direction)
- Path patterns: Chain of vertex and edge patterns
- Label expressions: IS label1|label2, omits for any label
- Anonymous patterns: () or -[]-> for unnamed elements

Examples:
- (n IS Person) -[e IS knows]-> (m IS Person)
- (n) -> (m)  # anonymous edge
- (n IS Person|Company)
"""

FILTERS_AND_CONDITIONS = """
Filters and Conditions:
- WHERE clause with boolean expressions
- Property access: variable.property
- Comparisons: =, <>, <, >, <=, >=
- Logical operators: AND, OR, NOT
- NULL checks: IS NULL, IS NOT NULL
- Pattern filters: vertex/edge labels, property values
- String matching: LIKE, REGEXP_LIKE
- IN predicate: value IN (list)

Example:
WHERE n.age > 25 AND n.name IS NOT NULL AND n.city IN ('NYC', 'LA')
"""

AGGREGATION_GROUPING = """
Grouping and Aggregation:
- GROUP BY expression, ...
- Aggregate functions: COUNT(*), COUNT(expr), SUM, AVG, MIN, MAX, LISTAGG
- DISTINCT modifier: COUNT(DISTINCT expr)
- Horizontal aggregation: Aggregates over group variables in paths
  - COUNT(e) for number of edges in path
  - SUM(e.weight) for total weight along path
  - ARRAY_AGG(e.amount) for list of amounts

Examples:
- SELECT COUNT(*) FROM GRAPH_TABLE(g MATCH (n IS Person) COLUMNS(1))
- SELECT n.name, COUNT(e) AS friends FROM GRAPH_TABLE(g MATCH (n) -[e]-> (m) COLUMNS(n.name)) GROUP BY n.name
- SELECT SUM(e.amount) FROM GRAPH_TABLE(g MATCH (n) -[e]->* (m) COLUMNS(e.amount))  # horizontal
"""

PATH_FINDING = """
Variable-Length Paths:
- Quantifiers: * (0+), + (1+), {n} (exactly n), {n,} (n+), {n,m} (n to m), {,m} (0 to m)
- Path finding: ANY, ANY SHORTEST, SHORTEST k, CHEAPEST k, ALL
- Path modes: WALK (any), TRAIL (no repeated edges), ACYCLIC (no repeated vertices), SIMPLE (no repeats except start/end)
- Cost functions: COST expression for cheapest paths

Examples:
- MATCH (n) -[e]->* (m)  # any path
- MATCH ANY SHORTEST (n) -[e]->* (m)  # shortest path
- MATCH SHORTEST 3 PATHS (n) -[e]->* (m)  # 3 shortest paths
- MATCH CHEAPEST 2 (n) -[e]->* (m) COST SUM(e.cost)  # 2 cheapest paths
"""

FUNCTIONS_OPERATORS = """
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

SYNTAX_RULES = """
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

ADVANCED_QUERY_PATTERNS = """
Advanced Query Patterns for Complex Queries:
- OPTIONAL MATCH: Left outer join for optional patterns
  - OPTIONAL MATCH (n) -[e:optional_rel]-> (m)
  - Variables from optional patterns may be null
- Subqueries:
  - EXISTS: Check if subquery returns results
    - WHERE EXISTS (SELECT 1 FROM GRAPH_TABLE(...) MATCH ...)
  - Scalar subqueries: Return single value
    - WHERE n.age > (SELECT AVG(age) FROM ...)
  - LATERAL subqueries: Reference outer variables
    - FROM LATERAL (SELECT ... FROM GRAPH_TABLE(...) WHERE outer_var = inner_var)
- Repeated variables: Same variable bound multiple times in pattern
  - (n) -[e1]-> (m) -[e2]-> (n)  # n bound twice
  - Use ALL_DIFFERENT(n, m) to prevent same binding
- Disconnected patterns: Multiple independent patterns in same MATCH
  - MATCH (a) -> (b), (c) -> (d)  # Cartesian product
- Number of rows per match:
  - ONE ROW PER VERTEX: Returns row per vertex in path
    - MATCH (n) -[e]->* (m) ONE ROW PER VERTEX (v) COLUMNS(v.id)
  - ONE ROW PER STEP: Returns row per edge in path
    - MATCH (n) -[e]->* (m) ONE ROW PER STEP (v1, e, v2) COLUMNS(v1.id, e.weight, v2.id)
- Path filters: WHERE clauses inside quantified patterns
  - MATCH (n) (-[e]-> WHERE e.weight > 5)* (m)
- Complex aggregations:
  - ARRAY_AGG with ordering: ARRAY_AGG(expr ORDER BY col)
  - LISTAGG with separator: LISTAGG(expr, '; ')
  - Window functions: Not in PGQL 2.1, but aggregations can be nested
- Advanced functions:
  - REGEXP_LIKE(string, pattern) for regex matching
  - ALL_DIFFERENT(v1, v2, v3) for ensuring distinct vertices/edges
  - VERTEX_EQUAL(v1, v2), EDGE_EQUAL(e1, e2) for equality
  - MATCHNUM() for match numbering in multi-match results
  - ELEMENT_NUMBER(v) for position in path

Examples:
- OPTIONAL MATCH: SELECT n.name, m.name FROM GRAPH_TABLE(g MATCH (n) OPTIONAL MATCH (n) -> (m) COLUMNS(n.name, m.name))
- EXISTS subquery: WHERE EXISTS (SELECT 1 FROM GRAPH_TABLE(g MATCH (n) -[e]-> (m) WHERE m.id = outer_m.id) COLUMNS(1))
- LATERAL: FROM GRAPH_TABLE(g MATCH (n) COLUMNS(n.id AS nid)), LATERAL (SELECT COUNT(*) FROM GRAPH_TABLE(g MATCH (nid) -> (m) COLUMNS(1)))
- ONE ROW PER STEP: MATCH (n) -[e]->+ (m) ONE ROW PER STEP (v1,e,v2) COLUMNS v1.id, e.amount, v2.id, SUM(e.amount) AS running_total
- Path with filter: MATCH ANY SHORTEST (n) (-[e]-> WHERE e.cost < 10)* (m)
"""
