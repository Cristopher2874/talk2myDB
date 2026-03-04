import textwrap

SQL_SCHEMA_DESCRIPTION = textwrap.dedent(
    """
    You are an expert Oracle SQL generator. The user asks questions about
    the power grid database schema which contains:

      • SUBSTATIONS(id, name, code, latitude, longitude, capacity_mva, status)
      • CIRCUITS(id, circuit_name, circuit_code, substation_id, voltage_kv, customers_served, avg_load_mw, peak_load_mw, neighborhood)
      • ASSETS(id, asset_id, asset_type, circuit_id, substation_id, condition_score, health_index, status, criticality)
      • CUSTOMERS(id, account_number, name, customer_type, circuit_id, avg_monthly_usage_kwh, peak_demand_kw, sla_priority)
      • OUTAGES(id, incident_code, circuit_id, root_cause_asset_id, start_time, end_time, cause_category, customers_affected, duration_minutes)
      • WORK_ORDERS(id, outage_id, asset_id, work_type, priority, status, labor_hours, material_cost)
      • DOCUMENTS(id, document_type, title, related_outage_id, related_asset_id, related_circuit_id, tags, author, document_date)
      • CREW_ASSIGNMENTS(crew_id, outage_id, dispatch_time, arrival_time)
      • CUSTOMER_COMPLAINTS(id, customer_id, outage_id, category, status, complaint_time, resolution)
      • ASSET_HEALTH_HISTORY(asset_id, reading_time, condition_score, temperature_c, load_pct)

    Key Relationships:
      CIRCUITS.substation_id = SUBSTATIONS.id
      ASSETS.circuit_id = CIRCUITS.id
      ASSETS.substation_id = SUBSTATIONS.id
      CUSTOMERS.circuit_id = CIRCUITS.id
      OUTAGES.circuit_id = CIRCUITS.id
      OUTAGES.root_cause_asset_id = ASSETS.id
      WORK_ORDERS.outage_id = OUTAGES.id
      WORK_ORDERS.asset_id = ASSETS.id
      DOCUMENTS.related_outage_id = OUTAGES.id
      DOCUMENTS.related_asset_id = ASSETS.id
      DOCUMENTS.related_circuit_id = CIRCUITS.id
      CREW_ASSIGNMENTS.outage_id = OUTAGES.id
      CUSTOMER_COMPLAINTS.customer_id = CUSTOMERS.id
      CUSTOMER_COMPLAINTS.outage_id = OUTAGES.id
      ASSET_HEALTH_HISTORY.asset_id = ASSETS.id

    Return valid SQL only. Your output will be directly fed to the oracle database.
    dont include backquotes as they would interfere
    """
)

SQL_FEW_SHOT_EXAMPLES = [
    {
        "q": "How many substations are there?",
        "sql": "SELECT COUNT(*) AS substation_count FROM substations;",
    },
    {
        "q": "What is the total capacity of all substations?",
        "sql": "SELECT SUM(capacity_mva) AS total_capacity_mva FROM substations;",
    },
    {
        "q": "List all circuits with their associated substations",
        "sql": (
            "SELECT c.circuit_name, s.name AS substation_name, c.voltage_kv, c.customers_served\n"
            "FROM circuits c\n"
            "JOIN substations s ON c.substation_id = s.id\n"
            "ORDER BY s.name, c.circuit_name;"
        ),
    },
    {
        "q": "Top 5 circuits by customer count",
        "sql": (
            "SELECT circuit_name, customers_served, neighborhood\n"
            "FROM circuits\n"
            "ORDER BY customers_served DESC FETCH FIRST 5 ROWS ONLY;"
        ),
    },
    {
        "q": "Assets by type and their average condition score",
        "sql": (
            "SELECT asset_type, COUNT(*) AS asset_count, AVG(condition_score) AS avg_condition\n"
            "FROM assets\n"
            "GROUP BY asset_type\n"
            "ORDER BY asset_count DESC;"
        ),
    },
]