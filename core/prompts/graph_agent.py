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
        "pgql": "SELECT COUNT(*) FROM graph_table (outage_network MATCH (s IS substation) COLUMNS (s.id))",
    },
    {
        "q": "How many circuits originate from a specific substation?",
        "pgql": (
            "SELECT COUNT(*)\n"
            "FROM graph_table (outage_network\n"
            "  MATCH (s IS substation) -[IS ORIGINATES_FROM]-> (c IS circuit)\n"
            "  WHERE s.id = 1\n"
            "  COLUMNS (c.id)\n"
            ")"
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
            "    s.name AS substation_name,\n"
            "    c.circuit_name AS circuit_name,\n"
            "    c.voltage_kv AS voltage_kv\n"
            "  )\n"
            ")"
        ),
    },
    {
        "q": "Assets located on circuits from a specific substation",
        "pgql": (
            "SELECT asset_id, asset_type, circuit_name, substation_name\n"
            "FROM graph_table (outage_network\n"
            "  MATCH (s IS substation) -[IS ORIGINATES_FROM]-> (c IS circuit) -[IS LOCATED_ON]-> (a IS asset)\n"
            "  COLUMNS (a.asset_id AS asset_id, a.asset_type AS asset_type, c.circuit_name AS circuit_name, s.name AS substation_name)\n"
            ")"
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
            "ORDER BY customer_count DESC"
        ),
    },
]