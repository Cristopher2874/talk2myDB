AGGREGATION_GROUPING_SKILL = {
    "name": "aggregation_grouping_skill",
    "description": "Provides information for grouping and aggregation in PGQL",
    "content": """
Grouping and Aggregation:
- GROUP BY expression, ...
- Aggregate functions: COUNT(*), COUNT(expr), SUM, AVG, MIN, MAX, LISTAGG
- DISTINCT modifier: COUNT(DISTINCT expr)
- Horizontal aggregation: Aggregates over group variables in paths
  - COUNT(e) for number of edges in path
  - SUM(e.weight) for total weight along path
  - ARRAY_AGG(e.amount) for list of amounts

Examples:
- GROUP BY with aggregation:
  Q: Count orders per customer
  PGQL:
  SELECT customer_name, COUNT(DISTINCT order_id) AS order_count
  FROM graph_table (graph_name
    MATCH (c IS Customer) -[IS PLACED]-> (o IS Order)
    COLUMNS (c.name AS customer_name, o.id AS order_id)
  )
  GROUP BY customer_name
  ORDER BY order_count DESC;

- Basic aggregation:
  SELECT COUNT(*) FROM GRAPH_TABLE(g MATCH (n IS Person) COLUMNS(1))
  SELECT n.name, COUNT(e) AS friends FROM GRAPH_TABLE(g MATCH (n) -[e]-> (m) COLUMNS(n.name)) GROUP BY n.name
  SELECT SUM(e.amount) FROM GRAPH_TABLE(g MATCH (n) -[e]->* (m) COLUMNS(e.amount))  # horizontal
"""
}
