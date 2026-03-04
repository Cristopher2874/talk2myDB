import textwrap

GRAPH_SCHEMA_DESCRIPTION = textwrap.dedent(
    """
    You are an expert Oracle SQL generator for property graphs. The user asks questions about
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
    """
)

GRAPH_FEW_SHOT_EXAMPLES = [
    {
        "q": "How many substations are there?",
        "pgql": (
            "SELECT COUNT(*)\n"
            "FROM graph_table (outage_network\n"
            "  MATCH (s IS substation)\n"
            "  COLUMNS (s.id)\n"
            ");"
        ),
    },
    {
        "q": "How many circuits originate from a specific substation?",
        "pgql": (
            "SELECT COUNT(*)\n"
            "FROM graph_table (outage_network\n"
            "  MATCH (s IS substation) -[IS ORIGINATES_FROM]-> (c IS circuit)\n"
            "  WHERE s.id = 1\n"
            "  COLUMNS (c.id)\n"
            ");"
        ),
    },
    {
        "q": "List all circuits and their originating substations",
        "pgql": (
            "SELECT substation_name, circuit_name, voltage_kv\n"
            "FROM GRAPH_TABLE (\n"
            "  outage_network\n"
            "  MATCH (s IS substation) -[IS ORIGINATES_FROM]-> (c IS circuit)\n"
            "  COLUMNS (\n"
            "    s.name         AS substation_name,\n"
            "    c.circuit_name AS circuit_name,\n"
            "    c.voltage_kv   AS voltage_kv\n"
            "  )\n"
            ");"
        ),
    },
    {
        "q": "Assets located on circuits from a specific substation",
        "pgql": (
            "SELECT asset_id, asset_type, circuit_name, substation_name\n"
            "FROM graph_table (outage_network\n"
            "  MATCH (s IS substation) -[IS ORIGINATES_FROM]-> (c IS circuit) -[IS LOCATED_ON]-> (a IS asset)\n"
            "  COLUMNS (a.asset_id AS asset_id, a.asset_type AS asset_type, c.circuit_name AS circuit_name, s.name AS substation_name)\n"
            ");"
        ),
    },
    {
        "q": "Customers served by circuits from each substation",
        "pgql": (
            "SELECT substation_name, COUNT(DISTINCT customer_id) AS customer_count\n"
            "FROM graph_table (outage_network\n"
            "  MATCH (s IS substation) -[IS ORIGINATES_FROM]-> (c IS circuit) -[IS SERVED_BY]-> (cust IS customer)\n"
            "  COLUMNS (s.name AS substation_name, cust.id AS customer_id)\n"
            ")\n"
            "GROUP BY substation_name\n"
            "ORDER BY customer_count DESC;"
        ),
    },
    {
        "q": "Outages and the circuits they affect",
        "pgql": (
            "SELECT incident_code, cause_category, circuit_name, substation_name\n"
            "FROM graph_table (outage_network\n"
            "  MATCH (o IS outage) -[IS AFFECTED]-> (c IS circuit) <-[IS ORIGINATES_FROM]- (s IS substation)\n"
            "  COLUMNS (o.incident_code AS incident_code, o.cause_category AS cause_category, c.circuit_name AS circuit_name, s.name AS substation_name)\n"
            ");"
        ),
    },
    {
        "q": "Assets that caused outages",
        "pgql": (
            "SELECT asset_id, asset_type, incident_code, cause_category, customers_affected\n"
            "FROM graph_table (outage_network\n"
            "  MATCH (o IS outage) -[IS CAUSED_BY]-> (a IS asset)\n"
            "  COLUMNS (a.asset_id AS asset_id, a.asset_type AS asset_type, o.incident_code AS incident_code, o.cause_category AS cause_category, o.customers_affected AS customers_affected)\n"
            ");"
        ),
    },
    {
        "q": "Work orders that address outages",
        "pgql": (
            "SELECT work_order_id, work_type, status, incident_code, cause_category\n"
            "FROM graph_table (outage_network\n"
            "  MATCH (w IS work_order) -[IS ADDRESSES]-> (o IS outage)\n"
            "  COLUMNS (w.id AS work_order_id, w.work_type AS work_type, w.status AS status, o.incident_code AS incident_code, o.cause_category AS cause_category)\n"
            ");"
        ),
    },
    {
        "q": "Assets serviced by work orders",
        "pgql": (
            "SELECT asset_id, asset_type, work_type, priority, status\n"
            "FROM graph_table (outage_network\n"
            "  MATCH (w IS work_order) -[IS SERVICES]-> (a IS asset)\n"
            "  COLUMNS (a.asset_id AS asset_id, a.asset_type AS asset_type, w.work_type AS work_type, w.priority AS priority, w.status AS status)\n"
            ");"
        ),
    },
    {
        "q": "Documents referencing outages",
        "pgql": (
            "SELECT title, document_type, incident_code, cause_category\n"
            "FROM graph_table (outage_network\n"
            "  MATCH (d IS document) -[IS REFERENCES_OUTAGE]-> (o IS outage)\n"
            "  COLUMNS (d.title AS title, d.document_type AS document_type, o.incident_code AS incident_code, o.cause_category AS cause_category)\n"
            ");"
        ),
    },
    {
        "q": "Customers affected by outages caused by assets on their circuit",
        "pgql": (
            "SELECT DISTINCT customer_name, customer_type, incident_code, asset_id, asset_type\n"
            "FROM graph_table (outage_network\n"
            "  MATCH (cust IS customer) <-[IS SERVED_BY]- (c IS circuit) <-[IS AFFECTED]- (o IS outage) -[IS CAUSED_BY]-> (a IS asset)\n"
            "  COLUMNS (cust.name AS customer_name, cust.customer_type AS customer_type, o.incident_code AS incident_code, a.asset_id AS asset_id, a.asset_type AS asset_type)\n"
            ");"
        ),
    },
    {
        "q": "Find all paths from substations to customers through circuits",
        "pgql": (
            "SELECT substation_name, circuit_name, customer_name, customer_type\n"
            "FROM graph_table (outage_network\n"
            "  MATCH (s IS substation) -[IS ORIGINATES_FROM]-> (c IS circuit) -[IS SERVED_BY]-> (cust IS customer)\n"
            "  COLUMNS (s.name AS substation_name, c.circuit_name AS circuit_name, cust.name AS customer_name, cust.customer_type AS customer_type)\n"
            ")\n"
            "ORDER BY substation_name, circuit_name;"
        ),
    },
    {
        "q": "Work orders servicing assets that caused outages",
        "pgql": (
            "SELECT work_order_id, work_type, asset_id, asset_type, incident_code, cause_category\n"
            "FROM graph_table (outage_network\n"
            "  MATCH (w IS work_order) -[IS SERVICES]-> (a IS asset) <-[IS CAUSED_BY]- (o IS outage)\n"
            "  COLUMNS (w.id AS work_order_id, w.work_type AS work_type, a.asset_id AS asset_id, a.asset_type AS asset_type, o.incident_code AS incident_code, o.cause_category AS cause_category)\n"
            ");"
        ),
    },
]