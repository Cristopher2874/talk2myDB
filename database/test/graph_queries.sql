-- ===================================================
-- GRAPH SQL QUERIES using p[ower] DB (for NL2Graph Agent)
-- ===================================================

-- Question: How many substations are there?
SELECT COUNT(*)
FROM graph_table (outage_network
  MATCH (s IS substation)
  COLUMNS (s.id)
);

-- Question: How many circuits originate from a specific substation?
SELECT COUNT(*)
FROM graph_table (outage_network
  MATCH (s IS substation) -[IS ORIGINATES_FROM]-> (c IS circuit)
  WHERE s.id = 1
  COLUMNS (c.id)
);

-- Question: List all circuits and their originating substations
SELECT substation_name, circuit_name, voltage_kv
FROM GRAPH_TABLE (
  outage_network
  MATCH (s IS substation) -[IS ORIGINATES_FROM]-> (c IS circuit)
  COLUMNS (
    s.name         AS substation_name,
    c.circuit_name AS circuit_name,
    c.voltage_kv   AS voltage_kv
  )
);

-- Question: Assets located on circuits from a specific substation
SELECT asset_id, asset_type, circuit_name, substation_name
FROM graph_table (outage_network
  MATCH (s IS substation) -[IS ORIGINATES_FROM]-> (c IS circuit) -[IS LOCATED_ON]-> (a IS asset)
  COLUMNS (a.asset_id AS asset_id, a.asset_type AS asset_type, c.circuit_name AS circuit_name, s.name AS substation_name)
);

-- Question: Customers served by circuits from each substation
SELECT substation_name, COUNT(DISTINCT customer_id) AS customer_count
FROM graph_table (outage_network
  MATCH (s IS substation) -[IS ORIGINATES_FROM]-> (c IS circuit) -[IS SERVED_BY]-> (cust IS customer)
  COLUMNS (s.name AS substation_name, cust.id AS customer_id)
)
GROUP BY substation_name
ORDER BY customer_count DESC;

-- Question: Outages and the circuits they affect
SELECT incident_code, cause_category, circuit_name, substation_name
FROM graph_table (outage_network
  MATCH (o IS outage) -[IS AFFECTED]-> (c IS circuit) <-[IS ORIGINATES_FROM]- (s IS substation)
  COLUMNS (o.incident_code AS incident_code, o.cause_category AS cause_category, c.circuit_name AS circuit_name, s.name AS substation_name)
);

-- Question: Assets that caused outages
SELECT asset_id, asset_type, incident_code, cause_category, customers_affected
FROM graph_table (outage_network
  MATCH (o IS outage) -[IS CAUSED_BY]-> (a IS asset)
  COLUMNS (a.asset_id AS asset_id, a.asset_type AS asset_type, o.incident_code AS incident_code, o.cause_category AS cause_category, o.customers_affected AS customers_affected)
);

-- Question: Work orders that address outages
SELECT work_order_id, work_type, status, incident_code, cause_category
FROM graph_table (outage_network
  MATCH (w IS work_order) -[IS ADDRESSES]-> (o IS outage)
  COLUMNS (w.id AS work_order_id, w.work_type AS work_type, w.status AS status, o.incident_code AS incident_code, o.cause_category AS cause_category)
);

-- Question: Assets serviced by work orders
SELECT asset_id, asset_type, work_type, priority, status
FROM graph_table (outage_network
  MATCH (w IS work_order) -[IS SERVICES]-> (a IS asset)
  COLUMNS (a.asset_id AS asset_id, a.asset_type AS asset_type, w.work_type AS work_type, w.priority AS priority, w.status AS status)
);

-- Question: Documents referencing outages
SELECT title, document_type, incident_code, cause_category
FROM graph_table (outage_network
  MATCH (d IS document) -[IS REFERENCES_OUTAGE]-> (o IS outage)
  COLUMNS (d.title AS title, d.document_type AS document_type, o.incident_code AS incident_code, o.cause_category AS cause_category)
);

-- Some advanced queries to test the limit of agent

-- Question: Customers affected by outages caused by assets on their circuit (2-hop query)
SELECT DISTINCT customer_name, customer_type, incident_code, asset_id, asset_type
FROM graph_table (outage_network
  MATCH (cust IS customer) <-[IS SERVED_BY]- (c IS circuit) <-[IS AFFECTED]- (o IS outage) -[IS CAUSED_BY]-> (a IS asset)
  COLUMNS (cust.name AS customer_name, cust.customer_type AS customer_type, o.incident_code AS incident_code, a.asset_id AS asset_id, a.asset_type AS asset_type)
);

-- Question: Customers connected through shared substations (3-hop cycle)
-- TODO: this is advanced path could work with the model?
SELECT DISTINCT customer1, customer2, shared_substation
FROM graph_table (outage_network
  MATCH (cust1 IS customer) <-[IS SERVED_BY]- (c1 IS circuit) <-[IS ORIGINATES_FROM]- (s IS substation)
        -[IS ORIGINATES_FROM]-> (c2 IS circuit) -[IS SERVED_BY]-> (cust2 IS customer)
  WHERE cust1.id != cust2.id
  COLUMNS (cust1.name AS customer1, cust2.name AS customer2, s.name AS shared_substation)
);

-- Complex queries

-- Question: Find all paths from substations to customers through circuits (2 hops)
SELECT substation_name, circuit_name, customer_name, customer_type
FROM graph_table (outage_network
  MATCH (s IS substation) -[IS ORIGINATES_FROM]-> (c IS circuit) -[IS SERVED_BY]-> (cust IS customer)
  COLUMNS (s.name AS substation_name, c.circuit_name AS circuit_name, cust.name AS customer_name, cust.customer_type AS customer_type)
)
ORDER BY substation_name, circuit_name;

-- Question: Outages with their root cause assets and affected customers (3-hop query)
-- TODO: chekc the direction of relations of the table
SELECT incident_code, cause_category, asset_id, asset_type, circuit_name, COUNT(DISTINCT customer_id) AS affected_customers
FROM graph_table (outage_network
  MATCH (o IS outage) -[IS CAUSED_BY]-> (a IS asset) <-[IS LOCATED_ON]- (c IS circuit) -[IS SERVED_BY]-> (cust IS customer)
  COLUMNS (o.incident_code AS incident_code, o.cause_category AS cause_category, a.asset_id AS asset_id, a.asset_type AS asset_type, c.circuit_name AS circuit_name, cust.id AS customer_id)
)
GROUP BY incident_code, cause_category, asset_id, asset_type, circuit_name
ORDER BY affected_customers DESC;

-- Question: Work orders servicing assets that caused outages (diamond pattern)
SELECT work_order_id, work_type, asset_id, asset_type, incident_code, cause_category
FROM graph_table (outage_network
  MATCH (w IS work_order) -[IS SERVICES]-> (a IS asset) <-[IS CAUSED_BY]- (o IS outage)
  COLUMNS (w.id AS work_order_id, w.work_type AS work_type, a.asset_id AS asset_id, a.asset_type AS asset_type, o.incident_code AS incident_code, o.cause_category AS cause_category)
);

-- Question: Complete incident analysis with all relationships
SELECT incident_code, start_time, cause_category, customers_affected,
       asset_id, asset_type, circuit_name, substation_name,
       affected_customer, customer_type,
       work_type, status, labor_hours,
       related_document
FROM graph_table (outage_network
  MATCH
    (o IS outage) -[IS AFFECTED]-> (c IS circuit) <-[IS ORIGINATES_FROM]- (s IS substation),
    (o) -[IS CAUSED_BY]-> (a IS asset) <-[IS LOCATED_ON]- (c),
    (c) -[IS SERVED_BY]-> (cust IS customer),
    (w IS work_order) -[IS ADDRESSES]-> (o),
    (w) -[IS SERVICES]-> (a),
    (d IS document) -[IS REFERENCES_OUTAGE]-> (o)
  COLUMNS (o.incident_code AS incident_code, o.start_time AS start_time, o.cause_category AS cause_category, o.customers_affected AS customers_affected,
           a.asset_id AS asset_id, a.asset_type AS asset_type, c.circuit_name AS circuit_name, s.name AS substation_name, cust.name AS affected_customer,
           cust.customer_type AS customer_type, w.work_type AS work_type, w.status AS status, w.labor_hours AS labor_hours, d.title AS related_document)
)
WHERE ROWNUM <= 20  -- Limit for performance
ORDER BY start_time DESC;
