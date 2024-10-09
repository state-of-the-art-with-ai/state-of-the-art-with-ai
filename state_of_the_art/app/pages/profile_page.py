import streamlit as st

from state_of_the_art.app.utils.login_utils import LoggedInUser
from state_of_the_art.tables.user_table import UserTable


user_data = LoggedInUser().get_user_data()

st.title("Profile")
name = st.text_input("Your Name", value=user_data.get('name', ''))
email = st.text_input("Email", value=user_data["email"])
prompt = st.text_area("About me prompt", value=user_data.get('prompt', ''))
password = st.text_input("Password", type="password", value=user_data["password_hash"])

st.markdown("### Email subscription preferences:")
daily_email_enabled = st.checkbox("Daily email", value=user_data.get('daily_email_enabled', True))
weekly_email_enabled = st.checkbox("Weekly email", value=user_data.get('weekly_email_enabled', True))
monthly_email_enabled = st.checkbox("Monthly email", value=user_data.get('monthly_email_enabled', True))

if st.button("Save Changes"):
    new_values = {
        'email': email,
        'prompt': prompt,
        'password_hash': password,
        'name': name,
        'daily_email_enabled': daily_email_enabled,
        'weekly_email_enabled': weekly_email_enabled,
        'monthly_email_enabled': monthly_email_enabled,
    }

    UserTable().update(by_key="tdw_uuid", by_value=user_data['tdw_uuid'], new_values=new_values)
    st.success("Changes saved successfully")
    st.rerun()
