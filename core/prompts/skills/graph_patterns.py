GRAPH_PATTERNS_SKILL = {
    "name": "graph_patterns_skill",
    "description": "Provides information for graph pattern matching in PGQL",
    "content": """
Graph Pattern Matching:
- Vertex patterns: (variable IS? label)
- Edge patterns: -[variable IS? label]-> (outgoing), <-[variable IS? label]- (incoming), -[variable IS? label]- (any direction)
- Path patterns: Chain of vertex and edge patterns
- Label expressions: IS label1|label2, omits for any label
- Anonymous patterns: () or -[]-> for unnamed elements

Examples:
- Multi-hop path matching:
  Q: Find customers who bought specific products
  PGQL:
  SELECT customer_name, product_name, order_date
  FROM graph_table (graph_name
    MATCH (cust IS Customer) -[IS PLACED]-> (o IS Order) -[IS CONTAINS]-> (p IS Product)
    WHERE p.name = 'Laptop'
    COLUMNS (cust.name AS customer_name, p.name AS product_name, o.date AS order_date)
  );

- Multi-match patterns:
  Q: Find reviews for products from their manufacturers
  PGQL:
  SELECT product_name, manufacturer_name, review_text, rating
  FROM graph_table (graph_name
    MATCH (p IS Product) <-[IS MANUFACTURES]- (m IS Manufacturer),
          (p) <-[IS REVIEWS]- (r IS Review)
    COLUMNS (p.name AS product_name, m.name AS manufacturer_name, r.text AS review_text, r.rating AS rating)
  );

- Basic patterns:
  (n IS Person) -[e IS knows]-> (m IS Person)
  (n) -> (m)  # anonymous edge
  (n IS Person|Company)
"""
}
