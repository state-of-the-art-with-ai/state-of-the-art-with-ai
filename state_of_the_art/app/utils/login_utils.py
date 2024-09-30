from state_of_the_art.tables.user_table import UserTable


import streamlit as st
from streamlit_cookies_manager import EncryptedCookieManager

cookies = None

def setup_login():
    global cookies 
    cookies = EncryptedCookieManager(
        # This prefix will get added to all your cookie names.
        # This way you can run your app on Streamlit Cloud without cookie name clashes with other apps.
        prefix="state-of-the-art-with-ai-750989039686.europe-west3.run.app",
        # You should really setup a long COOKIES_PASSWORD secret if you're running on Streamlit Cloud.
        password='1234',
    )
    if not cookies.ready():
        # Wait for the component to load and send us current cookies.
        st.stop()

    if not 'logged_in' in cookies or cookies['logged_in'] != 'True':
        # Create login form
        st.write('Please login')
        username = st.text_input('Username')
        password = st.text_input('Password', type='password')
        submit = st.button('Login')

        # Check if user is logged in
        if submit:
            if UserTable().check_password(username, password):
                cookies['username'] = username
                cookies['logged_in'] = 'True'
                cookies.save()
                st.rerun()
            else:
                st.warning('Invalid username or password')
        st.stop()
def logout():
    global cookies
    cookies['logged_in'] = 'False'
    cookies.save()
    st.success("Logged out")
    st.stop()
