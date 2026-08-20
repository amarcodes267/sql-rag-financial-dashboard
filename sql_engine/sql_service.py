from database.database import get_connection


def execute_query(query):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(query)

        rows = cursor.fetchall()

        result = [dict(row) for row in rows]

        return result

    finally:
        connection.close()


def get_all_financial_data():
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

    return execute_query(query)