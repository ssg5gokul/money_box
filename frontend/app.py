from logging import exception

import pandas as pd
import streamlit as st
from datetime import datetime
import requests

API_URL = "http://127.0.0.1:8000"

MAX_ROWS = 10

@st.cache_data
def get_schemes(mode):
    return requests.get(f"{API_URL}/savings_schemes/{mode}").json()

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
        selected_date = st.date_input("Enter Date", datetime(2024, 8, 1), label_visibility="collapsed")
        expense_response = requests.get(f"{API_URL}/expenses/{selected_date}")
        codes_response = requests.get(f"{API_URL}/savings_codes")

        try:
            expense_response.raise_for_status()
            codes_response.raise_for_status()
            existing_codes = codes_response.json()
            existing_expenses = expense_response.json()

        except requests.exceptions.HTTPError:
            st.error(f"{expense_response.status_code} - {expense_response.reason}")
            existing_expenses = []
            existing_codes = []

        categories = ["Rent", "Shopping", "Food", "Entertainment", "Savings", "Debts", "Other"]

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.header("Amount")

        with col2:
            st.header("Category")

        with col3:
            st.header("Reference")

        with col4:
            st.header("Notes")

        expenses = []
        codes = [code['investment_id'] for code in existing_codes]
        debts_accounts = [debt['debt_id'] for debt in get_debts()]

        for i in range(MAX_ROWS):
            if i < len(existing_expenses):
                amount = existing_expenses[i]['amount']
                category = existing_expenses[i]['category']
                ref = existing_expenses[i]['ref']
                notes = existing_expenses[i]['notes']

            else:
                amount = 0.0
                category = "Shopping"
                notes = ""

            with col1:
                amount_input = st.number_input("Amount", step=1.0, value=amount, key=f"amount_{selected_date}_{i}", label_visibility="collapsed")

            with col2:
                category_input = st.selectbox("Category", options=categories, index=categories.index(category),
                                              key=f"category_{selected_date}_{i}", label_visibility="collapsed")

            with col3:
                if category_input == 'Savings':
                    opt = codes
                    dis = False
                    ref_key = f"ref_savings_{selected_date}_{i}"

                elif category_input == 'Debts':
                    opt = debts_accounts
                    dis = False
                    ref_key = f"ref_debts_{selected_date}_{i}"

                else:
                    opt = ["NA"]
                    dis = True
                    ref_key = f"ref_others_{selected_date}_{i}"


                ref_input = st.selectbox("Reference", options=opt, index=0,
                                 key=ref_key, label_visibility="collapsed", disabled=dis)



            with col4:
                notes_input = st.text_input("Notes", value=notes, key=f"notes_{selected_date}_{i}",
                                            label_visibility="collapsed")

            expenses.append({
                'amount': float(amount_input),
                'category' : category_input,
                'ref': ref_input,
                'notes' : notes_input
            })

        submit_button = st.button("Submit", key=f"expense_{selected_date}")
        if submit_button:
            filtered_expense = [expense for expense in expenses if expense['amount'] > 0]
            try:
                requests.post(f"{API_URL}/expense/{selected_date}", json=filtered_expense)

            except requests.exceptions.HTTPError:
                st.error(f"{expense_response.status_code} - {expense_response.reason}")

    with tab_savings:
        selected_date = st.date_input("Enter Date", datetime(2024, 8, 1), label_visibility="collapsed", key="savings_date")

        saving_response = requests.get(f"{API_URL}/savings/{selected_date}")
        try:
            saving_response.raise_for_status()
            investments = saving_response.json()

        except requests.exceptions.HTTPError:
            st.error(f"{saving_response.status_code} - {saving_response.reason}")
            investments = []

        investment_modes = ["FD", "RD", "Mutual Funds", "Stocks", "ETF"]

        compounding_options = ["Yearly", "Half-yearly", "Quarterly", "Monthly", "Weekly", "Daily", "Continuously", "Not compounding until maturity", "NA"]


        col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

        with col1:
            st.text("Amount")

        with col2:
            st.text("Mode")

        with col3:
            st.text("Symbol")

        with col4:
            st.text("Compounding")

        with col5:
            st.text("No. of units")

        with col6:
            st.text("Return %")

        with col7:
            st.text("Duration(in days)")

        savings = []
        for i in range(MAX_ROWS):

            if i < len(investments):
                amt_invested = investments[i]['amt_invested']
                investment_mode = investments[i]['investment_mode']
                investment_id = investments[i]['investment_id']
                deposit_type = investments[i]['deposit_type']
                qty_units = investments[i]['qty_units']
                return_pct = investments[i]['return_pct']
                duration = investments[i]['duration']

            else:
                amt_invested = 0.0
                investment_mode = "FD"
                investment_id = "NA"
                deposit_type = "Not compounding until maturity"
                qty_units = 0.0
                return_pct = 0.0
                duration = 1

            with col1:
                amt_invested_input = st.number_input("Amount", step=1.0, value=amt_invested, key=f"amt_invested_{selected_date}_{i}",
                                               label_visibility="collapsed")

            with col2:
                key_mode = f"investment_modes_{selected_date}_{i}"
                investment_mode_input = st.selectbox("Investment Mode", options=investment_modes, index=investment_modes.index(investment_mode),
                                              key=key_mode, label_visibility="collapsed")

            with col3:
                if investment_mode_input not in ('Mutual Funds', 'Stocks'):
                    scheme_symbols_input = st.selectbox(label='Symbols', options=["NA"], disabled=True, label_visibility='collapsed', key=f"scheme_{selected_date}_{i}")
                    investment_id = "NA"
                else:
                    schemes = get_schemes(investment_mode_input)
                    opt = [f"{scheme['scheme_symbol']} - {scheme['scheme_name']}" for scheme in schemes]
                    scheme_symbols_input = st.selectbox(label='Symbols', options=opt, label_visibility='collapsed', key=f"scheme_{selected_date}_{i}")
                    investment_id = scheme_symbols_input.split("-")[0]



            with col4:
                if investment_mode_input in ('FD', 'RD'):
                    deposit_type = st.selectbox("Compounding", options=compounding_options, index= compounding_options.index(deposit_type), key=f"compounding_{selected_date}_{i}",
                                                label_visibility="collapsed")
                else:
                    st.selectbox("Compounding", options=compounding_options,
                                 index=compounding_options.index(deposit_type),
                                 key=f"compounding_{selected_date}_{i}",
                                 label_visibility="collapsed",
                                 disabled=True)

                    deposit_type = "NA"

            with col5:
                if investment_mode_input not in ('FD', 'RD'):
                    qty_units_input = st.number_input("No. of units", step=1.0, value=qty_units,
                                              key=f"qty_units_{selected_date}_{i}", label_visibility="collapsed")
                else:
                    st.number_input("No. of units", step=1.0, value=qty_units,
                                                      key=f"qty_units_{selected_date}_{i}",
                                                      label_visibility="collapsed",
                                                      disabled=True)
                    qty_units_input = 0.0


            with col6:
                if investment_mode_input in ('FD', 'RD'):
                    return_pct_input = st.number_input("Return %", step=1.0, value=return_pct, key=f"return_pct_{selected_date}_{i}",
                                            label_visibility="collapsed")
                else:
                    st.number_input("Return %", step=1.0, value=return_pct,
                                    key=f"return_pct_{selected_date}_{i}",
                                    label_visibility="collapsed",
                                    disabled=True)
                    return_pct_input = -1

            with col7:
                if investment_mode_input in ('FD', 'RD'):
                    duration_input = st.number_input("Duration", step=1, value=duration, key=f"duration_{selected_date}_{i}", label_visibility="collapsed")
                else:
                    st.number_input("Duration", step=1, value=duration, key=f"duration_{selected_date}_{i}", label_visibility="collapsed", disabled=True)
                    duration_input = -1


            savings.append({
                'amt_invested' : amt_invested_input,
                'investment_mode' : investment_mode_input,
                'investment_id' : investment_id,
                'deposit_type' : deposit_type,
                'qty_units' : qty_units_input,
                'return_pct' : return_pct_input,
                'duration' : duration_input
            })

        savings_submit_button = st.button("Submit")
        if savings_submit_button:
            filtered_savings = [s for s in savings if s['amt_invested'] > 0]

            try:
                savings_submit_response = requests.post(f"{API_URL}/savings/{selected_date}", json=filtered_savings)

            except requests.exceptions.HTTPError:
                st.error(f"{savings_submit_response.status_code} - {savings_submit_response.reason}")

    with tab_debts:
        debt_data = get_debts()
        required_columns = [
            "debt_id", "debt_type", "lender", "start_date", "principle_amount",
            "interest_rate", "duration_months", "interest_type",
            "description", "status"
        ]
        df = pd.DataFrame(debt_data, columns=required_columns)
        try:
            df.start_date = pd.to_datetime(df["start_date"], errors="coerce").dt.date
            df.end_date = pd.to_datetime(df["end_date"], errors="coerce").dt.date

        except KeyError as e:
            df.start_date = datetime(2020,1,1)
            df.end_date = datetime(2020,1,1)


        debt_types_opt = ['Home Loan', 'Personal Loan', 'Education Loan', 'Vehicle Loan', 'Gold Loan', 'Credit Card', 'Consumer Loan', 'Overdraft', 'Family/Friend', 'Other']
        status_opt = ['Active','Closed']
        interest_types_opt = ['Simple','Compounding','Reducing']

        st.subheader("Debt Summary")

        column_config = {
            "debt_id": st.column_config.TextColumn("Debt ID"),
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
        debt_date = st.date_input("Enter Date", datetime(2024, 8, 1), label_visibility="collapsed", key="debt_date")

        debt_transactions_response = requests.get(f"{API_URL}/debts_transactions/{debt_date}")

        try:
            debt_transactions_response.raise_for_status()
            debt_transactions = debt_transactions_response.json()

        except requests.exceptions.HTTPError:
            st.error(f"{debt_transactions_response.status_code} - {debt_transactions_response.reason}")
            debt_transactions = []

        debt_transactions_df = pd.DataFrame(debt_transactions)
        st.table(debt_transactions_df)



