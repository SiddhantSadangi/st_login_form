import streamlit as st
from st_supabase_connection import SupabaseConnection, execute_query
from stqdm import stqdm

from .auth import Authenticator


def hash_current_passwords(
    user_tablename: str = "users",
    username_col: str = "username",
    password_col: str = "password",
) -> None:
    """
    Hashes all current plaintext passwords stored in a database table (in-place).

    Args:
        user_tablename (str, optional): The name of the user table. Defaults to "users".
        username_col (str, optional): The column name for usernames. Defaults to "username".
        password_col (str, optional): The column name for passwords. Defaults to "password".

    Returns:
        None
    """

    # Initialize the Supabase connection
    client = st.connection(name="supabase", type=SupabaseConnection)
    auth = Authenticator()

    # Select usernames and plaintext passwords from the specified table
    user_pass_dicts = execute_query(
        client.table(user_tablename)
        .select(f"{username_col}, {password_col}")
        .not_.like(password_col, "$argon2id$%")
    ).data

    if len(user_pass_dicts) > 0:
        st.warning(f"Hashing {len(user_pass_dicts)} plaintext passwords.")
        # Iterate over each username-password pair, re-hash passwords, and update the table
        for pair in stqdm(user_pass_dicts):
            pair["password"] = auth.generate_pwd_hash(pair["password"])
            client.table(user_tablename).update({password_col: pair["password"]}).match(
                {username_col: pair["username"]}
            ).execute()
        st.success("All passwords hashed successfully.", icon="🔒")
    else:
        st.success("All passwords are already hashed.", icon="🔒")
