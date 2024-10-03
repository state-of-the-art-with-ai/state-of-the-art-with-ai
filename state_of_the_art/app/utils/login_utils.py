from state_of_the_art.tables.user_table import UserTable

cookies = None
def setup_login():
    import streamlit as st
    from streamlit_cookies_manager import EncryptedCookieManager
    global cookies 
    cookies = EncryptedCookieManager(
        prefix="state-of-the-art-with-ai-750989039686.europe-west3.run.app",
        # You should really setup a long COOKIES_PASSWORD secret if you're running on Streamlit Cloud.
        password='1234',
    )
    import time ; time.sleep(0.3)
    if not cookies.ready():
        # Wait for the component to load and send us current cookies.
        st.stop()

    if not 'logged_in' in cookies or cookies['logged_in'] != 'True':
        if st.query_params.get('page', False) == 'create_account':
            render_create_account_ui()
        else:
            render_loging_ui()
        st.stop()


def render_loging_ui():
    import streamlit as st
    st.write('Log in')
    email = st.text_input('E-mail')
    password = st.text_input('Password', type='password')

    c1, c2 = st.columns([1, 1])
    with c1:
        submit = st.button('Login')
        # Check if user is logged in
        if submit:
            with st.spinner("Logging in..."):
                try: 
                    if uuid := UserTable().authenticate_returning_uuid(email, password):
                        cookies['user_uuid'] = uuid
                        cookies['logged_in'] = 'True'
                        cookies.save()
                        import time ; time.sleep(0.1)
                        st.rerun()
                    else:
                        st.warning(f'Invalid username or password "{email}" "{password}"')
                except ValueError as e:
                    st.warning(str(e))
    
    with c2:
        st.text('Don\'t have an account?')
        st.link_button('Create account', '/?page=create_account')

def render_create_account_ui():
    import streamlit as st
    st.write('Create account')
    email = st.text_input('E-mail')
    password = st.text_input('Password', type='password')

    c1, c2 = st.columns([1, 2])
    with c1:
        if st.button('Create account'):
            st.session_state['create_account'] = True
            with st.spinner("Creating account..."):
                try:
                    uuid = UserTable().add_user(email, password)
                except ValueError as e:
                    st.warning(str(e))
                    return
                cookies['user_uuid'] = uuid
                cookies['logged_in'] = 'True'
                cookies.save()
                import time ; time.sleep(0.1)
                st.rerun()
    with c2:
        st.text('Already have an have an account?')
        st.link_button('Login', '/?page=login')


def logout():
    import streamlit as st
    global cookies
    cookies['logged_in'] = 'False'
    cookies.save()
    st.success("Logged out")
    st.rerun()


class LoggedInUser:
    
    @staticmethod
    def get_instance():
        return LoggedInUser()

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
