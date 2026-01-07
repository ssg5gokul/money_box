import pandas as pd
import streamlit as st
from datetime import datetime
import requests

API_URL = "http://127.0.0.1:8000"

MAX_ROWS = 10

@st.cache_data
def get_schemes():
    schemes_response = requests.get(f"{API_URL}/savings_schemes")
    try:
        schemes_response.raise_for_status()
        schemes = schemes_response.json()

    except requests.exceptions.HTTPError:
        st.error(f"{schemes_response.status_code} - {schemes_response.reason}")
        schemes = []

    return schemes

@st.cache_data
def get_investments():
    savings_response = requests.get(f"{API_URL}/savings")

    try:
        savings_response.raise_for_status()
        savings = savings_response.json()

    except requests.exceptions.HTTPError:
        st.error(f"{savings_response.status_code} - {savings_response.reason}")
        savings = []

    return savings


@st.cache_data
def get_debts():
    debt_response = requests.get(f"{API_URL}/debts")

    try:
        debt_response.raise_for_status()
        debts = debt_response.json()

    except requests.exceptions.HTTPError:
        st.error(f"{debt_response.status_code} - {debt_response.reason}")
        debts = []

    return debts


st.set_page_config(layout="wide")

st.title("Expense Management System")

tab_input, tab_analytics = st.tabs(["Add/Update", "Analytics"])


with tab_input:
    tab_expense, tab_savings, tab_debts = st.tabs(["Expense", "Savings", "Debts"])

    with tab_expense:
        selected_date = st.date_input("Enter Date", datetime.today(), label_visibility="collapsed")
        expense_response = requests.get(f"{API_URL}/expenses/{selected_date}")
        codes_response = requests.get(f"{API_URL}/savings_codes")

        try:
            expense_response.raise_for_status()
            codes_response.raise_for_status()
            existing_codes = codes_response.json()
            expense_data = expense_response.json()

        except requests.exceptions.HTTPError:
            st.error(f"{expense_response.status_code} - {expense_response.reason}")
            expense_data = []
            existing_codes = []


        categories = ["Rent", "Shopping", "Food", "Entertainment", "Savings", "Debts", "Other"]
        codes = [code['investment_id'] for code in existing_codes]
        debts_accounts = {debt['debt_id']:debt['debt_acc_num'] for debt in get_debts()}
        expenses = []

        expense_columns = [
            "id", "amount", "category",
            "ref_investment", "ref_debt", "notes"
        ]

        df = pd.DataFrame(expense_data, columns=expense_columns)

        expense_column_config = {
            "id": st.column_config.NumberColumn(
                "ID", step=1
            ),
            "amount": st.column_config.NumberColumn(
                "Amount", step=1
            ),
            "category": st.column_config.SelectboxColumn(
                "Category", options=categories
            ),
            "ref_investment": st.column_config.SelectboxColumn(
                "Investment reference", options=codes
            ),
            "ref_debt": st.column_config.SelectboxColumn(
                "Debt reference", options=debts_accounts.keys(), format_func=lambda x: debts_accounts.get(x)
            ),
            "notes": st.column_config.TextColumn("Description", default='None'),
        }

        expense_df = st.data_editor(
            df,
            column_config=expense_column_config,
            width='stretch',
            num_rows="dynamic"
        )

        if st.button("Submit", key='Expense_submit'):
            filtered_df = expense_df[expense_df["amount"] > 0]
            payload = filtered_df.copy()
            try:
                expense_df["expense_date"] = expense_df["expense_date"].astype(str)

            except KeyError as e:
                expense_df["expense_date"] = "2025-12-01"

            try:
                expense_submit_response = requests.post(
                    f"{API_URL}/expense/{selected_date}",
                    json=payload.to_dict(orient="records")
                )

                expense_submit_response.raise_for_status()
                st.success("Expenses saved successfully")

            except Exception as e:
                st.error(f"Failed to save Expenses - {e}")


    with tab_savings:
        savings_data = get_investments()
        schemes = get_schemes()

        savings_columns = [
            "investment_id", "start_date", "investment_code", "investment_mode", "amount_invested"
            "compounding", "return_pct", "duration", "qty_units"
        ]

        savings_df = pd.DataFrame(savings_data, columns=savings_columns)

        try:
            savings_df.start_date = pd.to_datetime(savings_df.start_date , errors="coerce").dt.date

        except TypeError:
            savings_df.start_date  = datetime(2020,1,1)

        compounding_opt = ['Daily','Quarterly','Monthly','Yearly','NA']

        investment_mode_opt = ['FD','RD','Stock','Mutual Funds','Others']

        investment_code_opt = [codes['scheme_symbol'] for codes in schemes]

        st.subheader("Savings Schemes")

        column_config = {
            "investment_id" : st.column_config.NumberColumn("ID", step=1),
            "start_date": st.column_config.DateColumn("Start Date"),
            "investment_code": st.column_config.SelectboxColumn("Stock /Mutual Fund codes", options=investment_code_opt),
            "investment_mode" : st.column_config.SelectboxColumn("Investment Mode", options=investment_mode_opt),
            "compounding" : st.column_config.SelectboxColumn("Compounding", options=compounding_opt),
            "return_pct" : st.column_config.NumberColumn("Return(%)", step=1.0),
            "duration" : st.column_config.NumberColumn("Duration(in months)", step=1),
            "qty_units" : st.column_config.NumberColumn("Units", step=1.0)

        }



    with tab_debts:
        debt_data = get_debts()
        debts_accounts = {debt['debt_id']: debt['debt_acc_num'] for debt in debt_data}
        required_columns = [
            "debt_id", "debt_acc_num", "debt_type", "lender", "start_date", "principle_amount",
            "interest_rate", "duration_months", "interest_type",
            "description", "status"
        ]
        df = pd.DataFrame(debt_data, columns=required_columns)

        try:
            df.start_date = pd.to_datetime(df["start_date"], errors="coerce").dt.date

        except KeyError as e:
            df.start_date = datetime(2020,1,1)


        debt_types_opt = ['Home Loan', 'Personal Loan', 'Education Loan', 'Vehicle Loan', 'Gold Loan', 'Credit Card', 'Consumer Loan', 'Overdraft', 'Family/Friend', 'Other']
        status_opt = ['Active','Closed']
        interest_types_opt = ['Simple','Compounding','Reducing']

        st.subheader("Debt Summary")

        column_config = {
            "id" : st.column_config.NumberColumn("ID", step = 1),
            "debt_acc_num": st.column_config.TextColumn("Debt Ac/No"),
            "debt_type": st.column_config.SelectboxColumn(
                "Debt Type", options=debt_types_opt
            ),
            "lender": st.column_config.TextColumn("Lender"),
            "start_date": st.column_config.DateColumn("Start Date"),
            "principle_amount": st.column_config.NumberColumn(
                "Principal Amount", step=1000.00
            ),
            "interest_rate": st.column_config.NumberColumn(
                "Interest Rate (%)", step=0.10
            ),
            "duration_months": st.column_config.NumberColumn(
                "Duration (Months)", step=1
            ),
            "interest_type": st.column_config.SelectboxColumn(
                "Interest Type", options=interest_types_opt
            ),
            "description": st.column_config.TextColumn("Description", default='None'),
            "status": st.column_config.SelectboxColumn(
                "Status", options=status_opt
            ),
        }

        edited_df = st.data_editor(
            df,
            column_config=column_config,
            width='stretch',
            num_rows="dynamic",
            hide_index=True
        )

        if st.button("Submit", key='Debts_submit'):
            filtered_df = edited_df[edited_df["principle_amount"] > 0]

            payload = filtered_df.copy()
            try:
                payload["start_date"] = payload["start_date"].astype(str)

            except KeyError as e:
                payload["start_date"] = datetime(2020,1,1)

            try:
                debt_submit_response = requests.post(
                    f"{API_URL}/debts",
                    json=payload.to_dict(orient="records")
                )
                debt_submit_response.raise_for_status()
                st.success("Debts saved successfully")
            except Exception as e:
                st.error(f"Failed to save debts - {e}")


        st.subheader("Debt Transactions")
        # debt_date = st.date_input("Enter Date", datetime.today(), label_visibility="collapsed", key="debt_date")
        debt_acc_sel = st.selectbox("Debt Account", options=debts_accounts.keys(), format_func=lambda x: debts_accounts.get(x), key="debt_acc_sel")

        debt_transactions_response = requests.get(f"{API_URL}/debts_transactions_by_acc/{debt_acc_sel}")

        try:
            debt_transactions_response.raise_for_status()
            debt_transactions = debt_transactions_response.json()

        except requests.exceptions.HTTPError:
            st.error(f"{debt_transactions_response.status_code} - {debt_transactions_response.reason}")
            debt_transactions = []

        debt_transactions_df = pd.DataFrame(debt_transactions)
        st.table(debt_transactions_df)



