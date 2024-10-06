import re
from typing import Union
from state_of_the_art.tables.base_table import BaseTable


class UserTable(BaseTable):
    table_name = "user"
    schema = {
        "email": {"type": str},
        "name": {"type": str},
        "password_hash": {"type": str},
        "prompt": {"type": str},
        "is_admin": {"type": bool},
    }

    def add_user(self, email: str, password: str, name: str) -> str:
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise ValueError(f"Invalid email pattern: {email}")
        if len(password) < 4:
            raise ValueError(f"Password is too short")

        df = self.read()
        if email in df["email"].values:
            raise ValueError(f"User with email {email} already exists")
        return self.add(email=email, password_hash=password, prompt="", name="", is_admin=False)

    def check_password_returning_uuid(self, email: str, given_password: str) ->Union[bool, str]:
        if not email:
            raise ValueError("Email is empty")
        if not given_password:
            raise ValueError("Password is empty")

        df = self.read()
        if email not in df["email"].values:
            return False

        password = df.loc[df["email"] == email, "password_hash"].values[0]
        if password == given_password:
            return df.loc[df["email"] == email, "tdw_uuid"].values[0]

        return False

    def toggle_admin(self, email: str):
        read = self.read()
        if 'is_admin' not in read.columns:
            is_admin = False
        else:
            is_admin = read.loc[read["email"] == email, "is_admin"].values[0]
        print("Current admin status", is_admin, "invert to", not is_admin)
        self.update(by_key="email", by_value=email, new_values={"is_admin": not is_admin})


    def find_user_by_uuid(self, uuid: str) -> 'UserEntity':
        df = self.read()
        data = df[df["tdw_uuid"] == uuid].iloc[0].to_dict()
        if not data:
            raise ValueError(f"User with uuid {uuid} not found")
        return UserEntity(data)

class UserEntity:
    def __init__(self, data) -> None:
        self.email = data["email"]
        self.name = data.get("name")
        self.tdw_uuid = data["tdw_uuid"]
    
    def get_name(self):
        return self.name
    
    def get_email(self):
        return self.email
    
    def get_uuid(self):
        return self.tdw_uuid
    
