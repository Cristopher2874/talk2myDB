import textwrap

GRAPH_SCHEMA_DESCRIPTION = textwrap.dedent(
    """
    You are an expert Oracle SQL generator for property graphs using PGQL. The user asks questions about
    the outage_network property graph, which represents the electrical grid infrastructure and outages:

    Vertices (Nodes):
      • SUBSTATION(id, name, code, latitude, longitude, capacity_mva, status)
      • CIRCUIT(id, circuit_name, circuit_code, voltage_kv, customers_served, avg_load_mw, peak_load_mw, neighborhood)
      • ASSET(id, asset_id, asset_type, condition_score, health_index, status, criticality, latitude, longitude, next_maintenance_due)
      • CUSTOMER(id, account_number, name, customer_type, sla_priority, avg_monthly_usage_kwh, latitude, longitude)
      • OUTAGE(id, incident_code, cause_category, weather_condition, customers_affected, duration_minutes, saidi_minutes, safi_count, start_time, end_time)
      • WORK_ORDER(id, work_type, priority, status, labor_hours, material_cost, created_time, completed_time)
      • DOCUMENT(id, document_type, title, tags, source, author, document_date)

    Edges (Relationships):
      • ORIGINATES_FROM: substations -> circuits (circuits originate from substations)
      • LOCATED_ON: circuits -> assets (assets are located on circuits)
      • SERVED_BY: circuits -> customers (customers are served by circuits)
      • AFFECTED: outages -> circuits (outages affect circuits)
      • CAUSED_BY: outages -> assets (outages are caused by assets)
      • ADDRESSES: work_orders -> outages (work orders address outages)
      • SERVICES: work_orders -> assets (work orders service assets)
      • REFERENCES_OUTAGE: documents -> outages (documents reference outages)
      • REFERENCES_ASSET: documents -> assets (documents reference assets)

    The graph represents the electrical grid infrastructure, customer connections, outage incidents, maintenance work, and related documentation.

    Use graph_table function with PGQL MATCH syntax for queries on the outage_network graph. Always return valid SQL only. Your output will be directly fed to the Oracle database.
    Do not include backquotes.

    The examples below are for reference only - they demonstrate general PGQL patterns.
    The actual database schema and data is provided above on DB description.
    """
)

GRAPH_FEW_SHOT_EXAMPLES = [
    {
        "q": "How many people are in the graph?",
        "pgql": (
            "SELECT COUNT(*)\n"
            "FROM graph_table (graph_name\n"
            "  MATCH (p IS Person)\n"
            "  COLUMNS (p.id)\n"
            ");"
        ),
    },
    {
        "q": "Find all employees who work for a specific company",
        "pgql": (
            "SELECT employee_name, company_name\n"
            "FROM graph_table (graph_name\n"
            "  MATCH (e IS Employee) -[IS WORKS_FOR]-> (c IS Company)\n"
            "  WHERE c.name = 'TechCorp'\n"
            "  COLUMNS (e.name AS employee_name, c.name AS company_name)\n"
            ");"
        ),
    },
    {
        "q": "Find customers who bought specific products",
        "pgql": (
            "SELECT customer_name, product_name, order_date\n"
            "FROM graph_table (graph_name\n"
            "  MATCH (cust IS Customer) -[IS PLACED]-> (o IS Order) -[IS CONTAINS]-> (p IS Product)\n"
            "  WHERE p.name = 'Laptop'\n"
            "  COLUMNS (cust.name AS customer_name, p.name AS product_name, o.date AS order_date)\n"
            ");"
        ),
    },
    {
        "q": "Count orders per customer",
        "pgql": (
            "SELECT customer_name, COUNT(DISTINCT order_id) AS order_count\n"
            "FROM graph_table (graph_name\n"
            "  MATCH (c IS Customer) -[IS PLACED]-> (o IS Order)\n"
            "  COLUMNS (c.name AS customer_name, o.id AS order_id)\n"
            ")\n"
            "GROUP BY customer_name\n"
            "ORDER BY order_count DESC;"
        ),
    },
    {
        "q": "Find users who follow each other (mutual following)",
        "pgql": (
            "SELECT u1_name, u2_name\n"
            "FROM graph_table (graph_name\n"
            "  MATCH (u1 IS User) -[IS FOLLOWS]-> (u2 IS User) -[IS FOLLOWS]-> (u1)\n"
            "  COLUMNS (u1.name AS u1_name, u2.name AS u2_name)\n"
            ");"
        ),
    },
    {
        "q": "Find customers connected through shared orders",
        "pgql": (
            "SELECT DISTINCT customer1, customer2, shared_order\n"
            "FROM graph_table (graph_name\n"
            "  MATCH (c1 IS Customer) -[IS PLACED]-> (o IS Order) <-[IS PLACED]- (c2 IS Customer)\n"
            "  WHERE c1.id != c2.id\n"
            "  COLUMNS (c1.name AS customer1, c2.name AS customer2, o.id AS shared_order)\n"
            ");"
        ),
    },
    {
        "q": "Find reviews for products from their manufacturers",
        "pgql": (
            "SELECT product_name, manufacturer_name, review_text, rating\n"
            "FROM graph_table (graph_name\n"
            "  MATCH (p IS Product) <-[IS MANUFACTURES]- (m IS Manufacturer),\n"
            "        (p) <-[IS REVIEWS]- (r IS Review)\n"
            "  COLUMNS (p.name AS product_name, m.name AS manufacturer_name, r.text AS review_text, r.rating AS rating)\n"
            ");"
        ),
    },
]
