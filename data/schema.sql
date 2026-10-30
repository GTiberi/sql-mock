PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS accounts;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS branches;

CREATE TABLE branches (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    city TEXT NOT NULL,
    region TEXT NOT NULL
);

CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    city TEXT NOT NULL,
    birth_date TEXT NOT NULL,
    signup_date TEXT NOT NULL,
    branch_id INTEGER NOT NULL REFERENCES branches(id)
);

CREATE TABLE accounts (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    branch_id INTEGER NOT NULL REFERENCES branches(id),
    account_type TEXT NOT NULL CHECK (account_type IN ('checking', 'savings', 'student')),
    opened_date TEXT NOT NULL,
    closed_date TEXT,
    status TEXT NOT NULL CHECK (status IN ('active', 'closed', 'suspended')),
    CHECK (closed_date IS NULL OR closed_date >= opened_date)
);

CREATE TABLE transactions (
    id INTEGER PRIMARY KEY,
    account_id INTEGER NOT NULL REFERENCES accounts(id),
    transaction_date TEXT NOT NULL,
    transaction_type TEXT NOT NULL CHECK (transaction_type IN ('debit', 'credit')),
    amount REAL NOT NULL CHECK (amount > 0),
    category TEXT,
    description TEXT,
    external_reference TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE INDEX idx_customers_branch ON customers(branch_id);
CREATE INDEX idx_accounts_customer ON accounts(customer_id);
CREATE INDEX idx_accounts_branch ON accounts(branch_id);
CREATE INDEX idx_transactions_account_date ON transactions(account_id, transaction_date);
CREATE INDEX idx_transactions_external_reference ON transactions(external_reference);

