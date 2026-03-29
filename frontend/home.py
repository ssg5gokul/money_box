import streamlit as st

st.set_page_config(
    page_title="Money Box",
    page_icon="💰",
    initial_sidebar_state="collapsed",
)

# Define app pages
landing_page = st.Page("input.py", title="Expense Management")
app_page = st.Page("analytics.py", title="Analytics")
admin_page = st.Page(
    "admin.py", title="Admin"
)

# Enables switch_page behaviour
if not st.user.is_logged_in:
    pg = st.navigation(
        [landing_page],
        position="hidden",
    )
elif st.user.is_logged_in == st.secrets["admin_email"]:
    pg = st.navigation(
        [app_page, admin_page],
    )
else:
    pg = st.navigation(
        [app_page],
        position="hidden",
    )

# Head to first page of navigation
pg.run()