CREATE TABLE IF NOT EXISTS companies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS financial_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER,
    year INTEGER,
    revenue REAL,
    operating_expense REAL,
    operating_income REAL,
    net_income REAL,
    total_assets REAL,
    total_liabilities REAL,
    total_equity REAL,
    operating_cash_flow REAL,
    FOREIGN KEY(company_id) REFERENCES companies(id)
);