from fastapi import FastAPI, Query
from datetime import date
import db_helper
from typing import List, Optional
from pydantic import BaseModel

app = FastAPI()


class Expenses(BaseModel):
    amount: float
    category: str
    notes: str


class Savings(BaseModel):
    amt_invested: float
    investment_mode: str
    scheme_symbols: str
    compounding: str
    qty_units: float
    return_pct: float
    duration: int


@app.get("/expenses/{expense_date}", response_model=List[Expenses])
def get_expenses_for_date(expense_date: date):
    expenses = db_helper.fetch_expense_records_for_date(expense_date)
    return expenses


@app.post("/expense/{expense_date}")
def put_expenses_for_date(expense_date: date, expenses: List[Expenses]):
    db_helper.delete_expense_for_date(expense_date)
    for expense in expenses:
        db_helper.insert_expense(expense_date, amount=expense.amount, category=expense.category, notes=expense.notes)

    return {"message": "Records updated successfully"}


@app.get("/expense_category")
def get_expenses_by_category(start_date: Optional[str] = Query(None), end_date: Optional[str] = Query(None)):
    expense_summary = db_helper.fetch_expense_summary_by_category(start_date, end_date)
    return expense_summary


@app.get("/expense_monthwise")
def get_expenses_by_category(year: int):
    expense_summary = db_helper.fetch_expense_summary_by_month([year])
    return expense_summary


# Savings
@app.get("/savings/{savings_date}", response_model=List[Savings])
def get_savings_for_date(savings_date: date):
    savings = db_helper.fetch_savings_records_for_date(savings_date)
    return savings


@app.post("/savings/{savings_date}")
def get_expenses_for_date(savings_date: date, savings: List[Savings]):
    db_helper.delete_savings_for_date(savings_date)
    for saving in savings:
        db_helper.insert_savings(date_=savings_date, amt_invested=saving.amt_invested,
                                 investment_mode=saving.investment_mode, scheme_symbols= saving.scheme_symbols,
                                 compounding= saving.compounding, qty_units= saving.qty_units,
                                 return_pct= saving.return_pct, duration= saving.duration)


    return {"message": "Records updated successfully"}


@app.get("/savings_schemes")
def get_schemes():
    schemes = db_helper.fetch_schemes()
    return schemes