import streamlit as st

from state_of_the_art.app.utils.login_utils import LoggedInUser
from state_of_the_art.tables.user_table import UserTable


user_data = LoggedInUser().get_user_data()

st.title("Profile page")
st.text("Authenticated user uuid: " + str(LoggedInUser.get_instance().get_uuid()))
st.text("User UUID: " + user_data['tdw_uuid'])
email = st.text_input("Email", value=user_data["email"])
prompt = st.text_area("About me prompt", value=user_data.get('prompt', ''))
password = st.text_input("Password", type="password", value=user_data["password_hash"])


if st.button("Save Changes"):
    UserTable().update(by_key="tdw_uuid", by_value=user_data['tdw_uuid'], new_values={'email': email, 'prompt': prompt, 'password_hash': password})
    st.success("Changes saved successfully")
    st.rerun()
