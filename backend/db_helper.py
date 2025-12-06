import mysql.connector
from contextlib import contextmanager
import my_logger

logger = my_logger.config_logger()


@contextmanager
def get_db_cursor(commit=False):
    connection = mysql.connector.connect(
        host="localhost",
        username="root",
        password="root",
        database="expense_manager"
    )

    if connection.is_connected():
        print("Connection successful")
    else:
        print("Failed to connect to DB.")

    cursor = connection.cursor(dictionary=True)

    yield cursor
    connection.commit()

    cursor.close()
    connection.close()

#expense DTO
def fetch_expense_all_records():
    with get_db_cursor() as cursor:
        cursor.execute("select * from expenses")
        expenses = cursor.fetchall()
        return expenses


def fetch_expense_records_for_date(expense_date):
    logger.info(f"Fetching expense records for the date: {expense_date}")
    with get_db_cursor() as cursor:
        cursor.execute("select * from expenses where expense_date=%s", (expense_date,))
        expenses = cursor.fetchall()
        return expenses


def insert_expense(expense_date, amount, category, notes):
    with get_db_cursor(commit=True) as cursor:
        cursor.execute("insert into expenses (expense_date, amount, category, notes) values (%s, %s, %s, %s)"
                       , (expense_date, amount, category, notes,))
        logger.debug(f"Inserted 1 row of expense record for the date: {expense_date}")


def delete_expense_for_date(expense_date):
    with get_db_cursor(commit=True) as cursor:
        cursor.execute("delete from expenses where expense_date = %s"
                       , (expense_date,))
        logger.debug(f"Deleted all the expense records for the date: {expense_date}")


def fetch_expense_summary_by_category(start_date, end_date):
    logger.info(f"Fetched category wise summary between {start_date} and {end_date}")
    with get_db_cursor() as cursor:
        cursor.execute("select category, sum(amount) as Amount from expenses where expense_date between %s "
                       "and %s group by category;",
                       (start_date, end_date))
        expenses_summary = cursor.fetchall()
        return expenses_summary


def fetch_expense_summary_by_month(year):
    logger.info(f"Fetching month wise summary for the year: {year}")
    with get_db_cursor() as cursor:
        cursor.execute("select month(expense_date) as Month, sum(amount) as Amount from expenses "
                       "where year(expense_date) = %s "
                       "group by month(expense_date) "
                       "order by month(expense_date);",
                       year)
        expenses_summary = cursor.fetchall()
        return expenses_summary


#savings DTO
def fetch_savings_records_for_date(date_):
    logger.info(f"Fetching savings records for the date: {date_}")
    with get_db_cursor() as cursor:
        cursor.execute("select * from savings_transactions where date=%s", (date_,))
        expenses = cursor.fetchall()
        return expenses


def fetch_all_savings_records():
    with get_db_cursor() as cursor:
        cursor.execute("select * from savings_transactions")
        expenses = cursor.fetchall()
        return expenses


def insert_savings(date_, amt_invested, investment_mode, scheme_symbols, compounding, qty_units, return_pct, duration):
    with get_db_cursor(commit=True) as cursor:
        cursor.execute("insert into savings_transactions (date, amt_invested, investment_mode, scheme_symbols, compounding, "
                       "qty_units, return_pct, duration) values (%s, %s, %s, %s, %s, %s, %s, %s)"
                       , (date_, amt_invested, investment_mode, scheme_symbols, compounding, qty_units, return_pct,
                          duration,))
        logger.debug(f"Inserted 1 row of savings record for the date: {date_}")

def delete_savings_for_date(date_):
    with get_db_cursor(commit=True) as cursor:
        cursor.execute("delete from savings_transactions where date = %s"
                       , (date_,))
        logger.debug(f"Deleted all the savings records for the date: {date_}")


def fetch_schemes():
    with get_db_cursor() as cursor:
        cursor.execute("select * from asset_master")
        expenses = cursor.fetchall()
        return list(expenses)


if __name__ == "__main__":
    pass