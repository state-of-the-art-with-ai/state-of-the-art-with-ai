from state_of_the_art.tables.user_table import UserTable


import streamlit as st
from streamlit_cookies_manager import EncryptedCookieManager

cookies = None
def setup_login():
    global cookies 
    cookies = EncryptedCookieManager(
        # This prefix will get added to all your cookie names.
        # This way you can run your app on Streamlit Cloud without cookie name clashes with other apps.
        prefix="state-of-the-art-with-ai-750989039686",
        # You should really setup a long COOKIES_PASSWORD secret if you're running on Streamlit Cloud.
        password='1234',
    )
    if not cookies.ready():
        # Wait for the component to load and send us current cookies.
        st.stop()

    if not 'logged_in' in cookies or cookies['logged_in'] != 'True':
        # Create login form
        st.write('Log in or Sign up')
        email = st.text_input('E-mail')
        password = st.text_input('Password', type='password')

        c1, c2, c3 = st.columns([1, 1, 3])
        with c1:
            submit = st.button('Login')
            # Check if user is logged in
            if submit:
                with st.spinner("Logging in..."):
                    if uuid:= UserTable().get_uuid_if_login_works(email, password):
                        cookies['user_uuid'] = uuid
                        cookies['logged_in'] = 'True'
                        cookies.save()
                        st.rerun()
                    else:
                        st.warning('Invalid username or password')
        
        with c2:
            st.text('Don\'t have an account?')
        with c3:
            if st.button('Create account'):
                with st.spinner("Creating account..."):
                    uuid = UserTable().add_user(email, password)
                    cookies['user_uuid'] = uuid
                    cookies['logged_in'] = 'True'
                    cookies.save()
                    st.rerun()
        st.stop()

def logout():
    global cookies
    cookies['logged_in'] = 'False'
    cookies.save()
    st.success("Logged out")
    st.rerun()


class LoggedInUser:
    def is_logged_in(self):
        global cookies
        return 'logged_in' in cookies and cookies['logged_in'] == 'True'
    
    def get_uuid(self) -> str:
        if not self.is_logged_in():
            raise ValueError("User is not logged in")
        global cookies
        return cookies['user_uuid']
    def get_user_data(self):
        user_uuid = self.get_uuid()
        user_df = UserTable().read()
        return user_df[user_df["tdw_uuid"] == user_uuid].iloc[0].to_dict()
    
    def is_admin(self):
        return self.get_user_data().get('is_admin', False)
