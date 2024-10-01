from state_of_the_art.tables.base_table import BaseTable


class UserTable(BaseTable):
    table_name = "user"
    schema = {
        "email": {"type": str},
        "password_hash": {"type": str},
        "prompt": {"type": str},
        "is_admin": {"type": bool},
    }

    def add_user(self, email: str, password: str) -> str:
        df = self.read()
        if email in df["email"].values:
            raise ValueError(f"User with email {email} already exists")
        return self.add(email=email, password_hash=password, prompt="", is_admin=False)

    def check_password(self, email: str, given_password: str) -> bool:
        df = self.read()
        if email not in df["email"].values:
            return False
        password = df.loc[df["email"] == email, "password_hash"].values[0]
        return password == given_password

    def get_uuid_if_login_works(self, email: str, given_password: str) -> bool:
        df = self.read()
        if email not in df["email"].values:
            return False
        password = df.loc[df["email"] == email, "password_hash"].values[0]
        if password == given_password:
            return df.loc[df["email"] == email, "tdw_uuid"].values[0]
        return None

    def list_users(self):
        return self.read().to_dict(orient="records")
    
    def toggle_admin(self, email: str):
        read = self.read()
        is_admin = read.loc[read["email"] == email, "is_admin"].values[0]
        self.update(by_key="email", by_value=email, new_values={"is_admin": not is_admin})


if __name__ == "__main__":
    import fire

    fire.Fire()
