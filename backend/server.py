import datetime

from fastapi import FastAPI, Query
from datetime import date
import db_helper
from typing import List, Optional, Literal
from pydantic import BaseModel

app = FastAPI()


class Expenses(BaseModel):
    id: int
    amount: float
    category: str
    ref_investment: Optional[str]
    ref_debt: Optional[int]
    notes: str


class Savings(BaseModel):
    investment_id: int
    start_date: date
    investment_code: str
    investment_mode: str
    amount_invested: float
    compounding: str
    qty_units: float
    return_pct: float
    duration: int

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


class Schemes(BaseModel):
    scheme_symbol: str
    scheme_name: str
    asset_type: Literal["Mutual Funds", "Stocks"]

# Expense DTO
@app.get("/expenses/{expense_date}", response_model=List[Expenses])
def get_expenses_for_date(expense_date: date):
    expenses = db_helper.fetch_expense_records_for_date(expense_date)
    return expenses

@app.post("/expense/{expense_date}")
def post_expenses_for_date(expense_date: date, expenses: List[Expenses]):
    for expense in expenses:
        db_helper.insert_expense(id=expense.id, expense_date= expense_date, amount=expense.amount, category=expense.category, ref_investment=expense.ref_investment, ref_debt = expense.ref_debt, notes=expense.notes)
        if expense.category == 'Debts':
            db_helper.insert_debt_transactions(ref=expense.ref_debt, date=expense_date, amount=expense.amount)

    return {"message": "Records updated successfully"}


@app.get("/expense_category")
def get_expenses_by_category(start_date: Optional[str] = Query(None), end_date: Optional[str] = Query(None)):
    expense_summary = db_helper.fetch_expense_summary_by_category(start_date, end_date)
    return expense_summary


@app.get("/expense_monthwise")
def get_expenses_by_month(year: int):
    expense_summary = db_helper.fetch_expense_summary_by_month([year])
    return expense_summary


# Savings DTO
@app.get("/savings", response_model=List[Savings])
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


@app.get("/savings_schemes")
def get_schemes():
    schemes = db_helper.fetch_schemes()
    return schemes


@app.get("/savings_codes")
def get_savings_codes():
    codes = db_helper.fetch_scheme_symbols()
    return codes

# Debts DTO
@app.get("/debts")
def get_debts():
    debts = db_helper.fetch_debts()
    return debts

@app.get("/debts_transactions_by_acc/{debt_id}")
def get_debts_by_acc(debt_id: int):
    debts = db_helper.fetch_debts_transactions_by_acc(debt_id)
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