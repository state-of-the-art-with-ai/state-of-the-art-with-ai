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
        st.write('Log in or Sign up')
        username = st.text_input('E-mail')
        password = st.text_input('Password', type='password')

        c1, c2, c3 = st.columns([1, 1, 3])
        with c1:
            submit = st.button('Login')
            # Check if user is logged in
            if submit:
                with st.spinner("Logging in..."):
                    if UserTable().check_password(username, password):
                        cookies['username'] = username
                        cookies['logged_in'] = 'True'
                        cookies.save()
                        st.rerun()
                    else:
                        st.warning('Invalid username or password')
        
        with c2:
            st.text('Don\'t have an account?')
        with c3:
            st.button('Create account')


        st.stop()
def logout():
    global cookies
    cookies['logged_in'] = 'False'
    cookies.save()
    st.success("Logged out")
    st.rerun()
