-- ===================================================
-- RELATIONAL SQL QUERIES in power DB
-- ===================================================

-- Question: How many substations are there?
SELECT COUNT(*) AS substation_count FROM substations;

-- Question: What is the total capacity of all substations?
SELECT SUM(capacity_mva) AS total_capacity_mva FROM substations;

-- Question: List all circuits with their associated substations
SELECT c.circuit_name, s.name AS substation_name, c.voltage_kv, c.customers_served
FROM circuits c
JOIN substations s ON c.substation_id = s.id
ORDER BY s.name, c.circuit_name;

-- Question: Top 5 circuits by customer count
SELECT circuit_name, customers_served, neighborhood
FROM circuits
ORDER BY customers_served DESC FETCH FIRST 5 ROWS ONLY;

-- Question: Assets by type and their average condition score
SELECT asset_type, COUNT(*) AS asset_count, AVG(condition_score) AS avg_condition
FROM assets
GROUP BY asset_type
ORDER BY asset_count DESC;

-- Question: Customers with highest monthly usage
SELECT name, customer_type, avg_monthly_usage_kwh, sla_priority
FROM customers
ORDER BY avg_monthly_usage_kwh DESC FETCH FIRST 10 ROWS ONLY;

-- Question: Outages by cause category
SELECT cause_category, COUNT(*) AS outage_count, AVG(duration_minutes) AS avg_duration
FROM outages
GROUP BY cause_category
ORDER BY outage_count DESC;

-- Question: Work orders by status and priority
SELECT status, priority, COUNT(*) AS order_count, SUM(labor_hours) AS total_hours
FROM work_orders
GROUP BY status, priority
ORDER BY status, priority;

-- Question: Find all customers affected by outages in the last 30 days
SELECT DISTINCT c.name, c.customer_type, o.incident_code, o.start_time, o.cause_category
FROM customers c
JOIN circuits cir ON c.circuit_id = cir.id
JOIN outages o ON o.circuit_id = cir.id
WHERE o.start_time >= SYSDATE - 30
ORDER BY o.start_time DESC;

-- Question: Assets requiring maintenance in the next 30 days
SELECT a.asset_id, a.asset_type, a.status, a.next_maintenance_due, s.name AS substation_name
FROM assets a
JOIN substations s ON a.substation_id = s.id
WHERE a.next_maintenance_due <= SYSDATE + 30
ORDER BY a.next_maintenance_due;

-- Some advanced queries

-- Question: Outages with work orders, showing costs and resolution times
SELECT o.incident_code, o.cause_category, o.customers_affected,
       w.work_type, w.priority, w.labor_hours, w.material_cost,
       (o.end_time - o.start_time) * 24 AS resolution_hours
FROM outages o
LEFT JOIN work_orders w ON o.id = w.outage_id
WHERE o.end_time IS NOT NULL
ORDER BY o.start_time DESC;

-- Question: Circuit reliability analysis with outage frequency
SELECT cir.circuit_name, cir.customers_served, cir.reliability_grade,
       COUNT(o.id) AS outage_count,
       AVG(o.duration_minutes) AS avg_outage_duration,
       SUM(o.customers_affected) AS total_customers_affected
FROM circuits cir
LEFT JOIN outages o ON cir.id = o.circuit_id
GROUP BY cir.id, cir.circuit_name, cir.customers_served, cir.reliability_grade
ORDER BY outage_count DESC, cir.customers_served DESC;

-- COMPLEX queries

-- Question: Customer complaints linked to outages
SELECT cc.category AS complaint_category, cc.status AS complaint_status,
       o.incident_code, o.cause_category, c.name AS customer_name, c.customer_type
FROM customer_complaints cc
JOIN customers c ON cc.customer_id = c.id
LEFT JOIN outages o ON cc.outage_id = o.id
ORDER BY cc.complaint_time DESC;

-- Question: Asset health trends (latest reading per asset)
SELECT a.asset_id, a.asset_type, h.condition_score, h.temperature_c, h.load_pct, h.reading_time
FROM assets a
JOIN asset_health_history h ON a.id = h.asset_id
WHERE h.reading_time = (SELECT MAX(reading_time) FROM asset_health_history WHERE asset_id = a.id)
ORDER BY h.condition_score DESC;

-- Question: Complete outage analysis with all related entities
SELECT o.incident_code, o.start_time, o.end_time, o.cause_category, o.customers_affected,
       cir.circuit_name, s.name AS substation_name,
       a.asset_id, a.asset_type,
       c.name AS affected_customer, c.customer_type,
       w.work_type, w.status, w.labor_hours, w.material_cost,
       d.title AS related_document
FROM outages o
JOIN circuits cir ON o.circuit_id = cir.id
JOIN substations s ON cir.substation_id = s.id
LEFT JOIN assets a ON o.root_cause_asset_id = a.id
LEFT JOIN customers c ON c.circuit_id = cir.id
LEFT JOIN work_orders w ON w.outage_id = o.id
LEFT JOIN documents d ON d.related_outage_id = o.id
WHERE ROWNUM <= 50  -- Limit for performance
ORDER BY o.start_time DESC;