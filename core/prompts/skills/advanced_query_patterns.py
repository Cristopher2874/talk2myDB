ADVANCED_QUERY_PATTERNS_SKILL = {
    "name": "advanced_query_patterns_skill",
    "description": "Provides information for advanced query patterns in PGQL",
    "content": """
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
- Bidirectional patterns (mutual relationships):
  Q: Find users who follow each other (mutual following)
  PGQL:
  SELECT u1_name, u2_name
  FROM graph_table (graph_name
    MATCH (u1 IS User) -[IS FOLLOWS]-> (u2 IS User) -[IS FOLLOWS]-> (u1)
    COLUMNS (u1.name AS u1_name, u2.name AS u2_name)
  );

- Bidirectional connections through shared entities:
  Q: Find customers connected through shared orders
  PGQL:
  SELECT DISTINCT customer1, customer2, shared_order
  FROM graph_table (graph_name
    MATCH (c1 IS Customer) -[IS PLACED]-> (o IS Order) <-[IS PLACED]- (c2 IS Customer)
    WHERE c1.id != c2.id
    COLUMNS (c1.name AS customer1, c2.name AS customer2, o.id AS shared_order)
  );

- OPTIONAL MATCH: SELECT n.name, m.name FROM GRAPH_TABLE(g MATCH (n) OPTIONAL MATCH (n) -> (m) COLUMNS(n.name, m.name))
- EXISTS subquery: WHERE EXISTS (SELECT 1 FROM GRAPH_TABLE(g MATCH (n) -[e]-> (m) WHERE m.id = outer_m.id) COLUMNS(1))
- LATERAL: FROM GRAPH_TABLE(g MATCH (n) COLUMNS(n.id AS nid)), LATERAL (SELECT COUNT(*) FROM GRAPH_TABLE(g MATCH (nid) -> (m) COLUMNS(1)))
- ONE ROW PER STEP: MATCH (n) -[e]->+ (m) ONE ROW PER STEP (v1,e,v2) COLUMNS v1.id, e.amount, v2.id, SUM(e.amount) AS running_total
- Path with filter: MATCH ANY SHORTEST (n) (-[e]-> WHERE e.cost < 10)* (m)
"""
}