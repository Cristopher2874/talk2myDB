BASIC_QUERY_SKILL = {
    "name": "basic_query_skill",
    "description": "Provides information for basic structure about simple PGQL statements",
    "content": """
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

Examples:
- Basic count query:
  Q: How many people are in the graph?
  PGQL:
  SELECT COUNT(*)
  FROM graph_table (graph_name
    MATCH (p IS Person)
    COLUMNS (p.id)
  );

- Degree calculation with aggregation:
  SELECT n.name, COUNT(e) AS degree
  FROM GRAPH_TABLE(my_graph MATCH (n) -[e]-> () COLUMNS(n.name))
  GROUP BY n.name
  ORDER BY degree DESC
"""
}
