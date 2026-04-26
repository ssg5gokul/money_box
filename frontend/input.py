import pandas as pd
import streamlit as st
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

from frontend.bootstrap import setup_project_root

setup_project_root()

from frontend.api_client import APIClient

TODAY = date.today()

st.set_page_config(layout="wide")

st.title("Expense Management System")

def show_maintenance_screen():
    st.markdown("""
        <div style="text-align:center; padding:50px;">
            <h1>🚧 Under Maintenance</h1>
            <p>We're currently unable to fetch data.</p>
            <p>Please try again after some time.</p>
        </div>
    """, unsafe_allow_html=True)

    st.stop()

tab_income, tab_expense, tab_savings, tab_debts = st.tabs(["Income", "Expense", "Savings", "Debts"])

with tab_income:
    current_month = [(TODAY - relativedelta (months = i)).strftime("%m-%Y") for i in range(3)]
    income_date = st.selectbox("Enter Month", options=current_month,
                               label_visibility="collapsed", key='income_date')
    #Income data
    try:
        income_response = APIClient(f'income/{income_date}')
        income_data = income_response.get_data(user_id=st.user.sub)

    except TimeoutError:
        show_maintenance_screen()

    except RuntimeError:
        st.error("Invalid data")

    income_columns = [
        "id", "date", "amount", "description"
    ]

    income_month = int(income_date.split('-')[0])
    income_yr = int(income_date.split('-')[1])
    st_date = date(income_yr,income_month,1)

    nxt_mnth = st_date.replace(day=28) + timedelta(days=4)
    nxt_mnth -= timedelta(days=nxt_mnth.day)

    income_df = pd.DataFrame(income_data, columns=income_columns)

    income_df.date = pd.to_datetime(income_df["date"]).dt.date

    income_column_config = {
        "id": st.column_config.NumberColumn(
            "ID", step=1, disabled=True
        ),
        "date" : st.column_config.DateColumn("Date", min_value=st_date, max_value=nxt_mnth),
        "amount": st.column_config.NumberColumn(
            "Amount", step=1.0
        ),
        "description": st.column_config.TextColumn(
            "Description", default='None')
    }

    income_edited_df = st.data_editor(
        income_df,
        column_config=income_column_config,
        width='stretch',
        num_rows="dynamic"
    )

    if st.button("Submit", key='Income_submit'):
        filtered_df = income_edited_df[income_edited_df["amount"] > 0]
        filtered_df["user_id"] = st.user.sub
        payload = filtered_df.copy()
        try:
            income_post = APIClient('income')
            income_post.post_data(payload)
            st.success("Income saved successfully")

        except Exception as e:
            st.error(f"Failed to save income - {e}")


with tab_expense:
    ninety_days_ago = TODAY - timedelta(days=90)
    selected_date = st.date_input("Enter Date", TODAY, min_value=ninety_days_ago, label_visibility="collapsed", key='expense_date')

    #Expense data
    expense_response = APIClient(f'expenses/{selected_date}')
    expense_data = expense_response.get_data(user_id=st.user.sub)

    #Equity/ETF symbols and Mutual funds codes
    codes_response = APIClient('current_investments')
    codes_data = codes_response.get_data(user_id=st.user.sub)
    codes = {code['investment_id']: code['investment'] for code in codes_data}

    #Loan accounts
    debt_response = APIClient('debts')
    debt_data = debt_response.get_data(user_id=st.user.sub)
    debts_accounts = {debt['debt_id']: debt['debt_acc_num'] for debt in debt_data}

    categories = ["Rent", "Shopping", "Food", "Entertainment", "Savings", "Debts", "Other"]

    expenses = []

    expense_columns = [
        "id", "amount", "category",
        "ref_investment", "ref_debt", "notes"
    ]

    expense_df = pd.DataFrame(expense_data, columns=expense_columns)

    expense_column_config = {
        "id": st.column_config.NumberColumn(
            "ID", step=1, disabled=True
        ),
        "amount": st.column_config.NumberColumn(
            "Amount", step=1
        ),
        "category": st.column_config.SelectboxColumn(
            "Category", options=categories
        ),
        "ref_investment": st.column_config.SelectboxColumn(
            "Investment reference", options=codes.keys(), format_func=lambda x: codes.get(x)
        ),
        "ref_debt": st.column_config.SelectboxColumn(
            "Debt reference", options=debts_accounts.keys(), format_func=lambda x: debts_accounts.get(x)
        ),
        "notes": st.column_config.TextColumn("Description", default='None'),
    }

    expense_edited_df = st.data_editor(
        expense_df,
        column_config=expense_column_config,
        width='stretch',
        num_rows="dynamic"
    )

    if st.button("Submit", key='Expense_submit'):
        filtered_df = expense_edited_df[expense_edited_df["amount"] > 0]
        filtered_df["user_id"] = st.user.sub
        payload = filtered_df.copy()
        try:
            expense_response.post_data(payload)
            st.success("Expenses saved successfully")

        except RuntimeError as e:
            st.error(f"Failed to save expense - {e}")


with tab_savings:
    #Investment data
    savings_response = APIClient('savings')
    savings_data = savings_response.get_data(user_id=st.user.sub)

    #Equity/ETF symbols and Mutual Funds codes
    schemes_response = APIClient('savings_schemes')
    schemes = schemes_response.get_data()
    market_code_opt = [codes['scheme_symbol'] for codes in schemes]

    savings_columns = [
        "investment_id", "start_date", "investment_mode", "deposit_account", "market_code",
        "compounding", "return_pct", "duration"
    ]

    savings_df = pd.DataFrame(savings_data, columns=savings_columns)

    try:
        savings_df.start_date = pd.to_datetime(savings_df.start_date , errors="coerce").dt.date

    except TypeError:
        savings_df.start_date  = datetime(2025,1,1)

    compounding_opt = ['Daily','Quarterly','Monthly','Yearly','NA']

    investment_mode_opt = ['FD','RD','Stocks','Mutual Funds','Others']

    st.subheader("Savings Schemes")

    savings_column_config = {
        "investment_id" : st.column_config.NumberColumn("ID", step=1),
        "start_date": st.column_config.DateColumn("Start Date"),
        "market_code" : st.column_config.SelectboxColumn("Stock /Mutual Fund codes", options=market_code_opt,default=None),
        "deposit_account": st.column_config.TextColumn("Deposit Account"),
        "investment_mode" : st.column_config.SelectboxColumn("Investment Mode", options=investment_mode_opt,default=None),
        "compounding" : st.column_config.SelectboxColumn("Compounding", options=compounding_opt, default=None),
        "return_pct" : st.column_config.NumberColumn("Return(%)", step=0.25, default=0.0),
        "duration" : st.column_config.NumberColumn("Duration(in months)", step=1, default=0)

    }

    savings_edited_df = st.data_editor(
       savings_df,
       column_config=savings_column_config,
       width='stretch',
       num_rows="dynamic",
       hide_index=True
    )


    if st.button("Submit", key='Savings_submit'):
        filtered_df = savings_edited_df[ ~( savings_edited_df["deposit_account"].isna() &
                        savings_edited_df["market_code"].isna())]
        filtered_df["user_id"] = st.user.sub
        payload = filtered_df.copy()
        try:
            payload["start_date"] = payload["start_date"].astype(str)

        except KeyError as e:
            payload["start_date"] = datetime(2025, 1, 1)

        try:
            savings_response.post_data(payload)
            st.success("Investments saved successfully")

        except RuntimeError as e:
            st.error(f"Failed to save investments - {e}")

    st.header("Savings Transactions")
    st.info("Newly added investments will be updated after the next data refresh.")
    # Equity/ETF symbols and Mutual funds codes
    codes_response = APIClient('current_investments')
    codes_data = codes_response.get_data(user_id=st.user.sub)
    codes = {code['investment_id']: code['investment'] for code in codes_data}


    investment_sel = st.selectbox("Savings Account/Code", options=codes, key="inv_acc_sel", format_func=lambda x: codes[x])

    # savings_trans_data = get_investment_transactions()
    savings_trans_response = APIClient(f'savings_transactions/{investment_sel if investment_sel else 0}')
    savings_trans_data = savings_trans_response.get_data()

    savings_trans_columns = [
        "transaction_id", "date", "investment_id",
        "amt_invested", "price_per_unit", "qty", "user"
    ]
    savings_trans_df = pd.DataFrame(savings_trans_data, columns=savings_trans_columns)

    st.table(savings_trans_df)

with tab_debts:
    #Loan details
    debt_response = APIClient('debts')
    debt_data = debt_response.get_data(user_id=st.user.sub)
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
            "Interest Rate (%)", step=0.25
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
        filtered_df["user_id"] = st.user.sub
        payload = filtered_df.copy()
        try:
            payload["start_date"] = payload["start_date"].astype(str)

        except KeyError as e:
            payload["start_date"] = datetime(2020,1,1)

        try:
            debt_response.post_data(payload)
            st.success("Loan details saved successfully")

        except RuntimeError as e:
            st.error(f"Failed to save loan details - {e}")


    st.subheader("Debt Transactions")

    debt_acc_sel = st.selectbox("Debt Account", options=debts_accounts.keys(), format_func=lambda x: debts_accounts.get(x), key="debt_acc_sel")

    #Loan EMI installments
    debt_trans_response = APIClient(f'debts_transactions_by_acc/{debt_acc_sel if debt_acc_sel else 0}')
    debt_transactions = debt_trans_response.get_data()

    debt_transactions_df = pd.DataFrame(debt_transactions)
    st.table(debt_transactions_df)



