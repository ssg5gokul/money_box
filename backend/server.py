import datetime

from fastapi import FastAPI, Query
from datetime import date
import db_helper
from typing import List, Optional, Literal
from pydantic import BaseModel

app = FastAPI()


class Expenses(BaseModel):
    amount: float
    category: str
    ref: str
    notes: str


class Savings(BaseModel):
    amt_invested: float
    investment_mode: str
    investment_id: str
    deposit_type: str
    qty_units: float
    return_pct: float
    duration: int

class Debt(BaseModel):
    debt_id: str
    debt_type: str
    lender: str
    start_date: str
    principle_amount: float
    interest_rate: float
    duration_months: int
    interest_type: str
    status: str
    description: str


class Schemes(BaseModel):
    scheme_symbol: str
    scheme_name: str
    asset_type: Literal["Mutual Funds", "Stocks"]


@app.get("/expenses/{expense_date}", response_model=List[Expenses])
def get_expenses_for_date(expense_date: date):
    expenses = db_helper.fetch_expense_records_for_date(expense_date)
    return expenses

@app.post("/expense/{expense_date}")
def post_expenses_for_date(expense_date: date, expenses: List[Expenses]):
    db_helper.delete_expense_for_date(expense_date)
    for expense in expenses:
        db_helper.insert_expense(expense_date, amount=expense.amount, category=expense.category, ref=expense.ref, notes=expense.notes)
        if expense.category == 'Debts':
            db_helper.insert_debt_transactions(expense.ref, expense_date, expense.amount)

    return {"message": "Records updated successfully"}


@app.get("/expense_category")
def get_expenses_by_category(start_date: Optional[str] = Query(None), end_date: Optional[str] = Query(None)):
    expense_summary = db_helper.fetch_expense_summary_by_category(start_date, end_date)
    return expense_summary


@app.get("/expense_monthwise")
def get_expenses_by_month(year: int):
    expense_summary = db_helper.fetch_expense_summary_by_month([year])
    return expense_summary


# Savings
@app.get("/savings/{savings_date}", response_model=List[Savings])
def get_savings_for_date(savings_date: date):
    savings = db_helper.fetch_savings_records_for_date(savings_date)
    return savings


@app.post("/savings/{savings_date}")
def post_savings_for_date(savings_date: date, savings: List[Savings]):
    db_helper.delete_savings_for_date(savings_date)
    for saving in savings:
        db_helper.insert_savings(date_=savings_date, amt_invested=saving.amt_invested,
                                 investment_mode=saving.investment_mode, investment_id= saving.investment_id,
                                 deposit_type= saving.deposit_type, qty_units= saving.qty_units,
                                 return_pct= saving.return_pct, duration= saving.duration)


    return {"message": "Records updated successfully"}


@app.get("/savings_schemes/{asset_type}")
def get_schemes(asset_type: Literal["Mutual Funds", "Stocks"]):
    schemes = db_helper.fetch_schemes(asset_type)
    return schemes


@app.get("/savings_codes")
def get_savings_codes():
    codes = db_helper.fetch_scheme_symbols()
    return codes

@app.get("/debts")
def get_debts():
    debts = db_helper.fetch_debts()
    return debts

@app.get("/debts_transactions/{debt_transaction_date}")
def get_debts(debt_transaction_date: date):
    debts = db_helper.fetch_debts_transactions(debt_transaction_date)
    return debts


@app.post("/debts")
def post_debts_for_date(debts: List[Debt]):
    db_helper.delete_debts()
    for debt in debts:
        db_helper.insert_debts(debt_id=debt.debt_id, debt_type = debt.debt_type, lender = debt.lender,
                               start_date = debt.start_date, principle_amount = debt.principle_amount,
                               interest_rate = debt.interest_rate, duration_months =debt.duration_months,
                               interest_type = debt.interest_type, description= debt.description, status= debt.status)



    return {"message": "Records updated successfully"}