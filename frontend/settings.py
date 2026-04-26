import streamlit as st
from bootstrap import setup_project_root

setup_project_root()

def login():
    if st.button("Log in"):
        st.user.is_logged_in = True
        st.rerun()


logout_page = st.Page("login.py", title="Log out", icon=":material/logout:")

entry_page = st.Page("input.py", title="Expense management", icon=":material/payments:")
analytics_page = st.Page("analytics.py", title="Analytics", icon=":material/analytics:")
login_page = st.Page("login.py", title="Login", icon=":material/login:")


if st.user.is_logged_in:
    pg = st.navigation(
        {
            "Account": [login_page],
            "Tools": [entry_page],
            "Reports": [analytics_page]
        }
    )
else:
    pg = st.navigation([login_page])

pg.run()