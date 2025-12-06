from backend import db_helper
import datetime

def test_fetch_records_for_date():
    data = db_helper.fetch_expense_records_for_date("2024-08-15")

    assert len(data) == 1
    assert data[0]["id"] == 62
    assert data[0]["expense_date"] == datetime.date(2024,8,15)
    assert data[0]["amount"] == 10