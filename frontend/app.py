import streamlit as st
from datetime import datetime
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(layout="wide")
st.title("Expense Management System")

tab_1, tab_2 = st.tabs(["Add/Update", "Analytics"])

with tab_1:
    selected_date = st.date_input("Enter Date", datetime(2024, 8, 1), label_visibility="collapsed")
    tab_a, tab_b = st.tabs(["Expense", "Savings"])

    with tab_a:
        response = requests.get(f"{API_URL}/expenses/{selected_date}")

        try:
            response.raise_for_status()
            existing_expenses = response.json()

        except requests.exceptions.HTTPError:
            st.error(f"{response.status_code} - {response.reason}")
            existing_expenses = []

        categories = ["Rent", "Shopping", "Food", "Entertainment", "Other"]

        with st.form(key="expense_form"):
            col1, col2, col3 = st.columns(3)

            with col1:
                st.header("Amount")

            with col2:
                st.header("Category")

            with col3:
                st.header("Notes")

            expenses = []
            for i in range(5):

                if i < len(existing_expenses):
                    amount = existing_expenses[i]['amount']
                    category = existing_expenses[i]['category']
                    notes = existing_expenses[i]['notes']

                else:
                    amount = 0.0
                    category = "Shopping"
                    notes = ""

                with col1:
                    amount_input = st.number_input("Amount", step=1.0, value=amount, key=f"amount_{selected_date}_{i}", label_visibility="collapsed")

                with col2:
                    category_input = st.selectbox("Category", options=categories, index=categories.index(category), key=f"category_{selected_date}_{i}", label_visibility="collapsed")

                with col3:
                    notes_input = st.text_input("Notes", value=notes, key=f"notes_{selected_date}_{i}", label_visibility="collapsed")

                expenses.append({
                    'amount': float(amount_input),
                    'category' : category_input,
                    'notes' : notes_input
                })

            submit_button = st.form_submit_button()
            if submit_button:
                filtered_expenses = [expense for expense in expenses if expense['amount'] > 0]

                try:
                    requests.post(f"{API_URL}/expense/{selected_date}", json=filtered_expenses)

                except requests.exceptions.HTTPError:
                    st.error(f"{response.status_code} - {response.reason}")

    with tab_b:
        response = requests.get(f"{API_URL}/savings/{selected_date}")
        schemes = requests.get(f"{API_URL}/savings_schemes").json()
        opt = [f"{scheme['scheme_symbol']} - {scheme['scheme_name']}" for scheme in schemes]
        try:
            response.raise_for_status()
            investments = response.json()

        except requests.exceptions.HTTPError:
            st.error(f"{response.status_code} - {response.reason}")
            investments = []

        investment_modes = ["FD", "RD", "Mutual Fund", "Stock", "ETF"]

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
        for i in range(5):

            if i < len(investments):
                amt_invested = investments[i]['amt_invested']
                investment_mode = investments[i]['investment_mode']
                scheme_symbols = investments[i]['scheme_symbols']
                compounding = investments[i]['compounding']
                qty_units = investments[i]['qty_units']
                return_pct = investments[i]['return_pct']
                duration = investments[i]['duration']

            else:
                amt_invested = 0.0
                investment_mode = "FD"
                scheme_symbols = "NA"
                compounding = "Not compounding until maturity"
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
                actual_mode = investment_mode_input

            with col3:
                scheme_symbols_input = st.selectbox(label='Symbols', options=opt, label_visibility='collapsed', key=f"scheme_{selected_date}_{i}")
                scheme_symbol = scheme_symbols_input.split("-")[0]
                # if actual_mode not in ('FD','RD'):
                #     scheme_symbols_input = st.text_input("Symbols", value=scheme_symbols, key=f"scheme_symbols_{selected_date}_{i}",
                #                             label_visibility="collapsed")
                #
                # else:
                #     scheme_symbols_input = st.text_input("Symbols", value="NA",
                #                                          key=f"scheme_symbols_{selected_date}_{i}",
                #                                          label_visibility="collapsed",
                #                                          disabled=True)


            with col4:
                if actual_mode in ('FD', 'RD'):
                    compounding_input = st.selectbox("Compounding", options=compounding_options, index= compounding_options.index(compounding), key=f"compounding_{selected_date}_{i}",
                                                   label_visibility="collapsed")
                else:
                    st.selectbox("Compounding", options=compounding_options,
                                                     index=compounding_options.index(compounding),
                                                     key=f"compounding_{selected_date}_{i}",
                                                     label_visibility="collapsed",
                                                     disabled=True)

                    compounding_input = "NA"

            with col5:
                if actual_mode not in ('FD', 'RD'):
                    qty_units_input = st.number_input("No. of units", step=1.0, value=qty_units,
                                              key=f"qty_units_{selected_date}_{i}", label_visibility="collapsed")
                else:
                    st.number_input("No. of units", step=1.0, value=qty_units,
                                                      key=f"qty_units_{selected_date}_{i}",
                                                      label_visibility="collapsed",
                                                      disabled=True)
                    qty_units_input = 0


            with col6:
                if actual_mode in ('FD', 'RD'):
                    return_pct_input = st.number_input("Return %", step=1.0, value=return_pct, key=f"return_pct_{selected_date}_{i}",
                                            label_visibility="collapsed")
                else:
                    st.number_input("Return %", step=1.0, value=return_pct,
                                    key=f"return_pct_{selected_date}_{i}",
                                    label_visibility="collapsed",
                                    disabled=True)
                    return_pct_input = -1

            with col7:
                if actual_mode in ('FD', 'RD'):
                    duration_input = st.number_input("Duration", step=1, value=duration, key=f"duration_{selected_date}_{i}", label_visibility="collapsed")
                else:
                    st.number_input("Duration", step=1, value=duration, key=f"duration_{selected_date}_{i}", label_visibility="collapsed", disabled=True)
                    duration_input = -1


            savings.append({
                'amt_invested' : amt_invested_input,
                'investment_mode' : investment_mode_input,
                'scheme_symbols' : scheme_symbol,
                'compounding' : compounding_input,
                'qty_units' : qty_units_input,
                'return_pct' : return_pct_input,
                'duration' : duration_input
            })

        savings_submit_button = st.button("Submit")
        if savings_submit_button:
            filtered_expenses = [s for s in savings if s['amt_invested'] > 0]

            try:
                requests.post(f"{API_URL}/savings/{selected_date}", json=filtered_expenses)

            except requests.exceptions.HTTPError:
                st.error(f"{response.status_code} - {response.reason}")