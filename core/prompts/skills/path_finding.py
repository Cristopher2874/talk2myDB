PATH_FINDING_SKILL = {
    "name": "path_finding_skill",
    "description": "Provides information for variable-length paths and path finding in PGQL",
    "content": """
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
}