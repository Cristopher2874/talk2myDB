FILTERS_AND_CONDITIONS_SKILL = {
    "name": "filters_and_conditions_skill",
    "description": "Provides information for filters and conditions in PGQL WHERE clauses",
    "content": """
Filters and Conditions:
- WHERE clause with boolean expressions
- Property access: variable.property
- Comparisons: =, <>, <, >, <=, >=
- Logical operators: AND, OR, NOT
- NULL checks: IS NULL, IS NOT NULL
- Pattern filters: vertex/edge labels, property values
- String matching: LIKE, REGEXP_LIKE
- IN predicate: value IN (list)

Examples:
- Filtering with WHERE clause:
  Q: Find all employees who work for a specific company
  PGQL:
  SELECT employee_name, company_name
  FROM graph_table (graph_name
    MATCH (e IS Employee) -[IS WORKS_FOR]-> (c IS Company)
    WHERE c.name = 'TechCorp'
    COLUMNS (e.name AS employee_name, c.name AS company_name)
  );

- Complex conditions:
  WHERE n.age > 25 AND n.name IS NOT NULL AND n.city IN ('NYC', 'LA')
"""
}
