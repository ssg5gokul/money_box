from contextlib import contextmanager
from dotenv import load_dotenv
import os
import mysql.connector
import my_logger

load_dotenv()

logger = my_logger.config_logger()


@contextmanager
def get_db_cursor(commit=False):
    connection = mysql.connector.connect(
        host=os.getenv("MYSQLHOST"),
        user=os.getenv("MYSQLUSER"),
        password=os.getenv("MYSQLPASSWORD"),
        database=os.getenv("MYSQL_DATABASE")
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
#
# def insert_expense(id, expense_date, amount, category, notes, ref_investment, ref_debt):
#     with get_db_cursor(commit=True) as cursor:
#         cursor.execute("INSERT INTO fact_expenses "
#                        "(id, expense_date, amount, category, notes, ref_investment, ref_debt) "
#                        "VALUES (%s, %s, %s, %s, %s, %s, %s) as new_data "
#                        "ON  DUPLICATE KEY UPDATE "
#                        "expense_date = new_data.expense_date, amount = new_data.amount, "
#                        "category = new_data.category, ref_investment = new_data.ref_investment, ref_debt = "
#                        "new_data.ref_debt, notes = new_data.notes;"
#                        , (id, expense_date, amount, category, notes, ref_investment, ref_debt,))
#         logger.debug(f"Inserted 1 row of expense record for the date: {expense_date}")


def insert_expense(id, expense_date, amount, category, notes, ref_investment, ref_debt):
    with get_db_cursor(commit=True) as cursor:
        cursor.callproc("populate_fact_expenses"
                       , (id, expense_date, amount, category, notes, ref_investment, ref_debt,))
        logger.debug(f"Inserted 1 row of expense record for the date: {expense_date}")

#savings DAO
def fetch_savings():
    with get_db_cursor() as cursor:
        cursor.execute("SELECT * FROM dim_investment_master")
        savings = cursor.fetchall()
        return savings

def insert_savings(investment_id, start_date, investment_mode, deposit_account, market_code,
                   compounding, return_pct, duration, qty_units):
    with get_db_cursor(commit=True) as cursor:
        cursor.execute("INSERT INTO dim_investment_master (investment_id, start_date, investment_mode,"
                       "deposit_account, market_code, compounding, return_pct, duration, qty_units) "
                       "VALUES (%s, %s, %s,%s, %s, %s, %s, %s, %s) as new_data "
                       "ON DUPLICATE KEY UPDATE start_date = new_data.start_date, investment_mode = "
                       "new_data.investment_mode, deposit_account = new_data.deposit_account, market_code = "
                       "new_data.market_code, compounding = new_data.compounding, "
                       "return_pct = new_data.return_pct, duration = new_data.duration, "
                       "qty_units = new_data.qty_units;"
                       , (investment_id, start_date, investment_mode, deposit_account, market_code,
                          compounding, return_pct, duration, qty_units, ))
        logger.debug(f"Inserted 1 row of savings record for the date: {start_date}")



# Savings Transactions DAO
def fetch_savings_transactions(inv_id):
    with get_db_cursor() as cursor:
        cursor.execute("select * from fact_investment_transactions where investment_id=%s",(inv_id,))
        savings_transactions = cursor.fetchall()
        return savings_transactions


def insert_savings_transaction(date, investment_id, amt_invested):
    with get_db_cursor(commit=True) as cursor:
        cursor.callproc("populate_fact_savings_installments", (investment_id, date, amt_invested, ))
        logger.debug(f"Inserted the following records - Date: {date}, Amount: {amt_invested}, Investment ID: {investment_id}.")

# Schemes and Symbols DAO
def fetch_schemes():
    with get_db_cursor() as cursor:
        cursor.execute("select * from dim_asset_master")
        expenses = cursor.fetchall()
        return list(expenses)




# Current investments DAO
def fetch_current_investments():
    with get_db_cursor() as cursor:
        cursor.execute("select investment_id, deposit_account as investment from dim_investment_master "
                       "where deposit_account is not null "
                       "union "
                       "select investment_id, market_code as investment from dim_investment_master "
                       "where market_code is not null ")
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
def fetch_debts_transactions_by_acc(debt_id):
    with get_db_cursor() as cursor:
        cursor.execute("select * from fact_debt_installments where debt_id=%s", (debt_id,))
        debts = cursor.fetchall()
        return debts

def insert_debt_transactions(date, amount, ref):
    with get_db_cursor(commit=True) as cursor:
        cursor.callproc("populate_fact_debt_installments", (ref, date, amount, ))
        logger.debug(f"Inserted the following records - Date: {date}, Amount: {amount}, Debt ID: {ref}.")


# Income DAO
def fetch_income(date):
    with get_db_cursor() as cursor:
        cursor.execute("SELECT * FROM dim_income where date_format(date,'%m-%Y') =%s;", params=(date,))
        debts = cursor.fetchall()
        return debts

def insert_income(id, date, amount, description):
    with (get_db_cursor(commit=True) as cursor):
        cursor.execute(
            "INSERT INTO dim_income (id, date, amount, description) "
            "VALUES (%s, %s, %s, %s) AS new_data"
            " ON DUPLICATE KEY UPDATE "
            "date = new_data.date, amount = new_data.amount, description = new_data.description"
            , (id, date, amount, description, ))
        logger.debug(f"Inserted 1 row of income for the date : {date}.")


if __name__ == "__main__":
    pass