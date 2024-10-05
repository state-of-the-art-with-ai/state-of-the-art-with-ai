from state_of_the_art.tables.user_table import UserTable
import streamlit as st
import time

class LoginInterface:
    @staticmethod
    def get_instance():
        if not hasattr(LoginInterface, 'instance'):
            LoginInterface.instance = LoginInterface()
        return LoginInterface.instance

    def __init__(self) -> None:
        from streamlit_cookies_manager import EncryptedCookieManager
        # This should be on top of your script
        cookies = EncryptedCookieManager(
            # This prefix will get added to all your cookie names.
            # This way you can run your app on Streamlit Cloud without cookie name clashes with other apps.
            prefix="my_sota_app",
            # You should really setup a long COOKIES_PASSWORD secret if you're running on Streamlit Cloud.
            password='123456',
        )
        while not cookies.ready():
            print("Waiting for cookies to be ready")
            time.sleep(0.3)
        print("Cookies are ready")
        self.cookies = cookies
        

    def logged_in(self):
        return self.cookies.get('logged_in') == "True"
    
    def get_uuid(self):
        return self.cookies.get('user_uuid')

    def register_login_state(self, user_uuid):
        self.cookies['logged_in'] = 'True'
        self.cookies['user_uuid'] = user_uuid
        
    def register_logout(self):
            self.cookies['logged_in'] = 'False'
            self.cookies['user_uuid'] = None

def setup_login():
    import streamlit as st
    if not LoginInterface.get_instance().logged_in():
        if st.query_params.get('page', False) == 'create_account':
            render_create_account_ui()
        else:
            render_loging_ui()
        st.stop()


def render_loging_ui():
    import streamlit as st
    st.markdown('### Log in')
    email = st.text_input('E-mail')
    password = st.text_input('Password', type='password')

    c1, c2 = st.columns([1, 1])
    with c1:
        submit = st.button('Login')
        # Check if user is logged in
        if submit:
            try: 
                if uuid := UserTable().check_password_returning_uuid(email, password):
                    LoginInterface.get_instance().register_login_state(uuid)
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
                LoginInterface.get_instance().register_login_state(uuid)
                import time ; time.sleep(0.1)
                st.rerun()
    with c2:
        st.text('Already have an have an account?')
        st.link_button('Login', '/?page=login')


def logout():
    import streamlit as st
    LoginInterface.get_instance().register_logout()
    st.success("Logged out")
    st.rerun()


class LoggedInUser:
    
    @staticmethod
    def get_instance():
        return LoggedInUser()

    def is_logged_in(self):
        return self.get_uuid() is not None
    
    def get_uuid(self) -> str:
        return LoginInterface.get_instance().get_uuid()

    def get_user_data(self):
        user_uuid = self.get_uuid()
        user_df = UserTable().read()
        return user_df[user_df["tdw_uuid"] == user_uuid].iloc[0].to_dict()
    
    def is_admin(self):
        return self.get_user_data().get('is_admin', False)
