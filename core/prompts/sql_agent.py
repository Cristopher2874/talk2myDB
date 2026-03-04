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
    {
        "q": "Outages by cause category",
        "sql": (
            "SELECT cause_category, COUNT(*) AS outage_count, AVG(duration_minutes) AS avg_duration\n"
            "FROM outages\n"
            "GROUP BY cause_category\n"
            "ORDER BY outage_count DESC;"
        ),
    },
    {
        "q": "Work orders by status and priority",
        "sql": (
            "SELECT status, priority, COUNT(*) AS order_count, SUM(labor_hours) AS total_hours\n"
            "FROM work_orders\n"
            "GROUP BY status, priority\n"
            "ORDER BY status, priority;"
        ),
    },
    {
        "q": "Find all customers affected by outages in the last 30 days",
        "sql": (
            "SELECT DISTINCT c.name, c.customer_type, o.incident_code, o.start_time, o.cause_category\n"
            "FROM customers c\n"
            "JOIN circuits cir ON c.circuit_id = cir.id\n"
            "JOIN outages o ON o.circuit_id = cir.id\n"
            "WHERE o.start_time >= SYSDATE - 30\n"
            "ORDER BY o.start_time DESC;"
        ),
    },
    {
        "q": "Assets requiring maintenance in the next 30 days",
        "sql": (
            "SELECT a.asset_id, a.asset_type, a.status, a.next_maintenance_due, s.name AS substation_name\n"
            "FROM assets a\n"
            "JOIN substations s ON a.substation_id = s.id\n"
            "WHERE a.next_maintenance_due <= SYSDATE + 30\n"
            "ORDER BY a.next_maintenance_due;"
        ),
    },
    {
        "q": "Outages with work orders, showing costs and resolution times",
        "sql": (
            "SELECT o.incident_code, o.cause_category, o.customers_affected,\n"
            "       w.work_type, w.priority, w.labor_hours, w.material_cost,\n"
            "       (o.end_time - o.start_time) * 24 AS resolution_hours\n"
            "FROM outages o\n"
            "LEFT JOIN work_orders w ON o.id = w.outage_id\n"
            "WHERE o.end_time IS NOT NULL\n"
            "ORDER BY o.start_time DESC;"
        ),
    },
    {
        "q": "Circuit reliability analysis with outage frequency",
        "sql": (
            "SELECT cir.circuit_name, cir.customers_served, cir.reliability_grade,\n"
            "       COUNT(o.id) AS outage_count,\n"
            "       AVG(o.duration_minutes) AS avg_outage_duration,\n"
            "       SUM(o.customers_affected) AS total_customers_affected\n"
            "FROM circuits cir\n"
            "LEFT JOIN outages o ON cir.id = o.circuit_id\n"
            "GROUP BY cir.id, cir.circuit_name, cir.customers_served, cir.reliability_grade\n"
            "ORDER BY outage_count DESC, cir.customers_served DESC;"
        ),
    },
    {
        "q": "Customer complaints linked to outages",
        "sql": (
            "SELECT cc.category AS complaint_category, cc.status AS complaint_status,\n"
            "       o.incident_code, o.cause_category, c.name AS customer_name, c.customer_type\n"
            "FROM customer_complaints cc\n"
            "JOIN customers c ON cc.customer_id = c.id\n"
            "LEFT JOIN outages o ON cc.outage_id = o.id\n"
            "ORDER BY cc.complaint_time DESC;"
        ),
    },
    {
        "q": "Asset health trends (latest reading per asset)",
        "sql": (
            "SELECT a.asset_id, a.asset_type, h.condition_score, h.temperature_c, h.load_pct, h.reading_time\n"
            "FROM assets a\n"
            "JOIN asset_health_history h ON a.id = h.asset_id\n"
            "WHERE h.reading_time = (SELECT MAX(reading_time) FROM asset_health_history WHERE asset_id = a.id)\n"
            "ORDER BY h.condition_score DESC;"
        ),
    },
]