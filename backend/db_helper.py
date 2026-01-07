import mysql.connector
from contextlib import contextmanager
import my_logger

logger = my_logger.config_logger()


@contextmanager
def get_db_cursor(commit=False):
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="expense_manager"
    )

    if connection.is_connected():
        print("DB Connection is established")

    else:
        print("DB Connection couldn't be established")

    cursor = connection.cursor(dictionary=True)

    try:
        yield cursor
        if commit:
            connection.commit()

    except Exception:
        connection.rollback()
        print("Database transaction failed")
        raise

    finally:
        cursor.close()
        connection.close()

#eExpense DAO
def fetch_expense_records_for_date(expense_date):
    logger.info(f"Fetching expense records for the date: {expense_date}")
    with get_db_cursor() as cursor:
        cursor.execute("select * from fact_expenses where expense_date=%s", (expense_date,))
        expenses = cursor.fetchall()
        return expenses


def insert_expense(id, expense_date, amount, category, notes, ref_investment, ref_debt):
    with get_db_cursor(commit=True) as cursor:
        cursor.execute("INSERT INTO fact_expenses "
                       "(id, expense_date, amount, category, notes, ref_investment, ref_debt) "
                       "VALUES (%s, %s, %s, %s, %s, %s, %s) as new_data "
                       "ON  DUPLICATE KEY UPDATE "
                       "expense_date = new_data.expense_date, amount = new_data.amount, "
                       "category = new_data.category, ref_investment = new_data.ref_investment, ref_debt = "
                       "new_data.ref_debt, notes = new_data.notes;"
                       , (id, expense_date, amount, category, notes, ref_investment, ref_debt,))
        logger.debug(f"Inserted 1 row of expense record for the date: {expense_date}")


# def fetch_expense_summary_by_category(start_date, end_date):
#     logger.info(f"Fetched category wise summary between {start_date} and {end_date}")
#     with get_db_cursor() as cursor:
#         cursor.execute("select category, sum(amount) as Amount "
#                        "from dim_expenses "
#                        "where expense_date between %s and %s "
#                        "group by category;",
#                        (start_date, end_date))
#         expenses_summary = cursor.fetchall()
#         return expenses_summary
#
#
# def fetch_expense_summary_by_month(year):
#     logger.info(f"Fetching month wise summary for the year: {year}")
#     with get_db_cursor() as cursor:
#         cursor.execute("select month(expense_date) as Month, sum(amount) as Amount from dim_expenses "
#                        "where year(expense_date) = %s "
#                        "group by month(expense_date) "
#                        "order by month(expense_date);",
#                        year)
#         expenses_summary = cursor.fetchall()
#         return expenses_summary


#savings DAO
def fetch_savings():
    with get_db_cursor() as cursor:
        cursor.execute("SELECT * FROM dim_investment_master")
        savings = cursor.fetchall()
        return savings

def fetch_savings_records_for_date(date_):
    logger.info(f"Fetching savings records for the date: {date_}")
    with get_db_cursor() as cursor:
        cursor.execute("select * from fact_investment_transactions where date=%s", (date_,))
        expenses = cursor.fetchall()
        return expenses


def fetch_all_savings_records():
    with get_db_cursor() as cursor:
        cursor.execute("select * from fact_investment_transactions")
        expenses = cursor.fetchall()
        return expenses


def insert_savings(date_, amt_invested, investment_mode, investment_id, deposit_type, qty_units, return_pct, duration):
    with get_db_cursor(commit=True) as cursor:
        cursor.execute("insert into dim_investment_master (investment_mode, investment_id, deposit_type, "
                       "qty_units, return_pct, duration) values (%s, %s, %s, %s, %s, %s, %s, %s)"
                       , (date_, amt_invested, investment_mode, investment_id, deposit_type, qty_units, return_pct,
                          duration,))
        logger.debug(f"Inserted 1 row of savings record for the date: {date_}")

def delete_savings_for_date(date_):
    with get_db_cursor(commit=True) as cursor:
        cursor.execute("delete from savings_transactions where date = %s"
                       , (date_,))
        logger.debug(f"Deleted all the savings records for the date: {date_}")


def fetch_schemes():
    with get_db_cursor() as cursor:
        cursor.execute("select * from dim_asset_master")
        expenses = cursor.fetchall()
        return list(expenses)


def fetch_scheme_symbols():
    with get_db_cursor() as cursor:
        cursor.execute("select distinct trim(scheme_symbol) as investment_id, scheme_name, investment_mode "
                       "from dim_investment_master f left join dim_asset_master a "
                       "on trim(f.investment_code) = trim(a.scheme_symbol);")
        codes = cursor.fetchall()
        return list(codes)

#Debt DAO
def fetch_debts():
    with get_db_cursor() as cursor:
        cursor.execute("select * from dim_debt_master where status='Active';")
        debts = cursor.fetchall()
        return debts

def insert_debts(debt_id, debt_acc_num, debt_type, lender, start_date, principle_amount, interest_rate, duration_months, interest_type, description, status):
    with (get_db_cursor(commit=True) as cursor):
        cursor.execute(
            "INSERT INTO dim_debt_master (debt_id, debt_acc_num, debt_type, lender, start_date, principle_amount, "
            "interest_rate, duration_months, interest_type, description, status) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) AS new_data"
            " ON DUPLICATE KEY UPDATE "
            "debt_acc_num = new_data.debt_acc_num, debt_type = new_data.debt_type, lender = new_data.lender, "
            "start_date = new_data.start_date, principle_amount = new_data.principle_amount, interest_rate = new_data.interest_rate,"
            "duration_months = new_data.duration_months, interest_type = new_data.interest_type,"
            "description = new_data.description, status = new_data.status"
            , (debt_id, debt_acc_num, debt_type, lender, start_date, principle_amount, interest_rate, duration_months, interest_type, description, status))
        logger.debug(f"Inserted 1 row of debt record with ID : {debt_acc_num}.")


# Debts transactions DAO
def fetch_debts_transactions(date_):
    with get_db_cursor() as cursor:
        cursor.execute("select * from fact_debt_installments where installment_date=%s", (date_,))
        debts = cursor.fetchall()
        return debts


def fetch_debts_transactions_by_acc(debt_id):
    with get_db_cursor() as cursor:
        cursor.execute("select * from fact_debt_installments where debt_id=%s", (debt_id,))
        debts = cursor.fetchall()
        return debts

def insert_debt_transactions(date, amount, ref):
    with get_db_cursor(commit=True) as cursor:
        cursor.callproc("populate_fact_debt_installments", (ref, date, amount,))
        logger.debug(f"Inserted the following records - Date: {date}, Amount: {amount}, Debt ID: {ref}.")

if __name__ == "__main__":
    pass