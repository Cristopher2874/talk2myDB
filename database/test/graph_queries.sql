-- ===================================================
-- GRAPH SQL QUERIES using graph_table (for NL2Graph Agent)
-- ===================================================
-- Question: How many accounts are there?
SELECT COUNT(*) FROM graph_table (BANK_GRAPH MATCH (a) COLUMNS (a.id));

-- Question: What is the total amount transferred?
SELECT SUM(amount) FROM graph_table (BANK_GRAPH MATCH (src) -[e IS BANK_TRANSFERS]-> (dst) COLUMNS (e.amount AS amount));

-- Question: Top 5 accounts by number of incoming transfers
SELECT id, name, COUNT(*) AS incoming_transfers
FROM graph_table (BANK_GRAPH MATCH (src) -[e IS BANK_TRANSFERS]-> (a) COLUMNS (a.id AS id, a.name AS name))
GROUP BY id, name
ORDER BY incoming_transfers DESC FETCH FIRST 5 ROWS ONLY;

-- Question: Which accounts received transfers from account 387 in 1 to 3 hops?
SELECT DISTINCT id, name
FROM graph_table (BANK_GRAPH MATCH (src) -[IS BANK_TRANSFERS]->{1,3} (a) WHERE src.id = 387 COLUMNS (a.id AS id, a.name AS name));

-- Question: Accounts with circular transfers (3-hop cycles)
SELECT DISTINCT id, name
FROM graph_table (BANK_GRAPH MATCH (a) -[IS BANK_TRANSFERS]->{3} (a) COLUMNS (a.id AS id, a.name AS name));

-- Question: Total amount received by account 387
SELECT SUM(amount) AS total_received
FROM graph_table (BANK_GRAPH MATCH (src) -[e IS BANK_TRANSFERS]-> (a) WHERE a.id = 387 COLUMNS (e.amount AS amount));
