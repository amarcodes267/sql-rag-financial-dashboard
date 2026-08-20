import sqlite3
from pathlib import Path

DATABASE_PATH = Path("data/financial.db")


def get_connection():
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    return connection


def initialize_database():
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    """)

    cursor.execute("""
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
        )
    """)

    connection.commit()
    connection.close()


def insert_company(name):
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        "INSERT OR IGNORE INTO companies (name) VALUES (?)",
        (name,)
    )

    connection.commit()

    cursor.execute(
        "SELECT id FROM companies WHERE name = ?",
        (name,)
    )

    company_id = cursor.fetchone()["id"]

    connection.close()

    return company_id


def insert_financial_data(company_id, data):
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO financial_data (
            company_id,
            year,
            revenue,
            operating_expense,
            operating_income,
            net_income,
            total_assets,
            total_liabilities,
            total_equity,
            operating_cash_flow
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        company_id,
        data.get("year"),
        data.get("revenue"),
        data.get("operating_expense"),
        data.get("operating_income"),
        data.get("net_income"),
        data.get("total_assets"),
        data.get("total_liabilities"),
        data.get("total_equity"),
        data.get("operating_cash_flow")
    ))

    connection.commit()
    connection.close()


def get_financial_data():
    connection = get_connection()

    query = """
        SELECT
            c.name AS company,
            f.year,
            f.revenue,
            f.operating_expense,
            f.operating_income,
            f.net_income,
            f.total_assets,
            f.total_liabilities,
            f.total_equity,
            f.operating_cash_flow
        FROM financial_data f
        JOIN companies c
        ON f.company_id = c.id
        ORDER BY f.year
    """

    data = connection.execute(query).fetchall()

    connection.close()

    return [dict(row) for row in data]