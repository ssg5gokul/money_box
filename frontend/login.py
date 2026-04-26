from api_client import APIClient
import streamlit as st
import pandas as pd

def add_user():
    user_df = pd.DataFrame({
        'user_id': st.user.sub,
        'fname': st.user.given_name,
        'lname': st.user.family_name,
        'email': st.user.email,
        'created_at': st.user.updated_at
    }, index=[0])

    try:
        users_api = APIClient("users")

        if users_api.get_data(user_id=st.user.sub)['user_count'] == 0:
            users_api.post_data(user_df)

    except TimeoutError:
        st.info("Apologies for the inconvenience. Couldn't fetch your data at the moment due to a maintenance window. Please try later.")

    except RuntimeError:
        st.error("Invalid data")

st.title("Welcome to Money Box! 🐖")
st.subheader("Track. Save. Grow your money smarter.")

# 1. CHECK LOGIN STATUS
if not st.user.is_logged_in:
    st.write("\n")
    if st.button(
            "Sign up to the Money Box",
            type="primary",
            key="checkout-button",
            use_container_width=True,
    ):
        st.login("auth0")

    with st.expander("📝 Privacy & Data Security Disclaimer"):
        st.markdown("""
This is a personal portfolio project currently in development. To ensure your security, I use Auth0 for authentication so that I never see or store your passwords.\n
**Data Usage:** Your email is only used to create a session and demonstrate the app's features. It will not be shared or used for any other purpose.\n
**Account Deletion:** If you would like your data removed, please submit a request using the link below and I will manually delete your record from the system.\n
**Feedback:** As this is a live project, you might encounter bugs. Please feel free to report them via the link below!
        """)
else:
    # 2. LOGGED IN UI
    st.success(f"Logged in as {st.user.email}")
    add_user()

    with st.expander("⚙️ Account Settings"):
        st.warning("Action below is permanent.")
        if st.button("Delete My Account Data", type="secondary", use_container_width=True):
            # For a resume project, a simple 'Contact' redirect or a success message is best
            st.error("Request Sent! Since this is a demo, please email progoks123@gmail.com to confirm deletion.")
            # st.logout() # Optional: kick them out after they click delete

    if st.button("Log out"):
        st.logout()

# Always show the footer
st.divider()
st.link_button(
    "Report any issues here:",
    url="https://github.com/ssg5gokul/money_box/issues",
    icon=":material/bug_report:"
)

