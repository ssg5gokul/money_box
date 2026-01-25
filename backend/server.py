from fastapi import FastAPI
from datetime import date
import db_helper
from typing import List, Optional, Literal
from pydantic import BaseModel

app = FastAPI()


class Expenses(BaseModel):
    id: Optional[int] = None
    amount: float
    category: str
    ref_investment: Optional[int]
    ref_debt: Optional[int]
    notes: str

class Savings(BaseModel):
    investment_id: Optional[int] = None
    start_date: date
    investment_mode: str
    deposit_account: Optional[str] = None
    market_code: Optional[str] = None
    compounding: Optional[str] = None
    return_pct: float 
    duration: int  
    qty_units: Optional[float] = None

class Debt(BaseModel):
    debt_id: int
    debt_acc_num: str
    debt_type: str
    lender: str
    start_date: str
    principle_amount: float
    interest_rate: float
    duration_months: int
    interest_type: str
    status: str
    description: str

class SavingsTransactions(BaseModel):
    transaction_id: Optional[int]=None
    date: date
    investment_id: int
    amt_invested: float
    current_price_per_unit: float
    qty: Optional[float] = None


class Schemes(BaseModel):
    scheme_symbol: str
    scheme_name: str
    asset_type: Literal["Mutual Funds", "Stocks"]

# Expense DTO
@app.get("/expenses/{expense_date}", response_model=List[Expenses])
def get_expenses_for_date(expense_date: date):
    expenses = db_helper.fetch_expense_records_for_date(expense_date)
    return expenses


@app.post("/expenses/{expense_date}")
def post_expenses_for_date(expense_date: date, expenses: List[Expenses]):
    for expense in expenses:
        db_helper.insert_expense(id=expense.id, expense_date=expense_date, amount=expense.amount,
                                 category=expense.category, ref_investment=expense.ref_investment,
                                 ref_debt=expense.ref_debt, notes=expense.notes)

        # if expense.category == 'Debts':
        #     db_helper.insert_debt_transactions(ref=expense.ref_debt, date=expense_date, amount=expense.amount)
        #
        # elif expense.category == 'Savings':
        #     db_helper.insert_savings_transaction(date=expense_date, investment_id=expense.ref_investment,
        #                                          amt_invested=expense.amount)


    return {"message": "Records updated successfully"}


# @app.get("/expense_category")
# def get_expenses_by_category(start_date: Optional[str] = Query(None), end_date: Optional[str] = Query(None)):
#     expense_summary = db_helper.fetch_expense_summary_by_category(start_date, end_date)
#     return expense_summary
#
#
# @app.get("/expense_monthwise")
# def get_expenses_by_month(year: int):
#     expense_summary = db_helper.fetch_expense_summary_by_month([year])
#     return expense_summary


# Savings DTO
@app.get("/savings", response_model=List[Savings])
def get_savings():
    savings = db_helper.fetch_savings()
    return savings


@app.post("/savings")
def post_savings(savings: List[Savings]):
    for saving in savings:
        db_helper.insert_savings(investment_id = saving.investment_id, start_date = saving.start_date,
                                 investment_mode = saving.investment_mode,
                                 deposit_account = saving.deposit_account, market_code = saving.market_code,
                                 compounding = saving.compounding, return_pct = saving.return_pct,
                                 duration = saving.duration, qty_units = saving.qty_units)

    return {"message": "Records updated successfully"}

@app.get("/savings_transactions/{inv_id}", response_model=List[SavingsTransactions])
def get_savings_transactions(inv_id: int):
    savings = db_helper.fetch_savings_transactions(inv_id)
    return savings


@app.post("/savings_transactions")
def post_savings_transactions(savings_transactions: List[SavingsTransactions]):
    for saving_transaction in savings_transactions:
        db_helper.insert_savings_transaction(date= saving_transaction.date,
                    investment_id= saving_transaction.investment_id, amt_invested= saving_transaction.amt_invested)

    return {"message": "Records updated successfully"}

# Savings codes and accounts
@app.get("/savings_schemes")
def get_schemes():
    schemes = db_helper.fetch_schemes()
    return schemes


@app.get("/current_investments")
def get_deposit_accounts():
    codes = db_helper.fetch_current_investments()
    return codes

# Debts DTO
@app.get("/debts")
def get_debts():
    debts = db_helper.fetch_debts()
    return debts

@app.post("/debts")
def post_debts_for_date(debts: List[Debt]):
    for debt in debts:
        db_helper.insert_debts(debt_id = debt.debt_id,
                               debt_acc_num=debt.debt_acc_num, debt_type = debt.debt_type, lender = debt.lender,
                               start_date = debt.start_date, principle_amount = debt.principle_amount,
                               interest_rate = debt.interest_rate, duration_months =debt.duration_months,
                               interest_type = debt.interest_type, description= debt.description, status= debt.status)



    return {"message": "Records updated successfully"}

@app.get("/debts_transactions_by_acc/{debt_id}")
def get_debts_by_acc(debt_id: int):
    debts = db_helper.fetch_debts_transactions_by_acc(debt_id)
    return debts
