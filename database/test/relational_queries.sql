-- ===================================================
-- RELATIONAL SQL QUERIES (for NL2SQL Agent)
-- ===================================================

-- Question: How many accounts are there?
SELECT COUNT(*) AS account_count FROM BANK_ACCOUNTS;

-- Question: What is the total amount transferred?
SELECT SUM(amount) AS total_amount FROM BANK_TRANSFERS;

-- Question: Top 5 accounts by balance
SELECT name, balance
FROM BANK_ACCOUNTS
ORDER BY balance DESC FETCH FIRST 5 ROWS ONLY;

-- Question: Accounts with more than 20 incoming transfers
SELECT a.name, COUNT(t.txn_id) AS incoming_transfers
FROM BANK_ACCOUNTS a JOIN BANK_TRANSFERS t ON a.id = t.dst_acct_id
GROUP BY a.name
HAVING COUNT(t.txn_id) > 20
ORDER BY incoming_transfers DESC;

-- Question: Total balance of all accounts
SELECT SUM(balance) AS total_balance FROM BANK_ACCOUNTS;

-- Question: Average transfer amount
SELECT AVG(amount) AS avg_transfer FROM BANK_TRANSFERS;