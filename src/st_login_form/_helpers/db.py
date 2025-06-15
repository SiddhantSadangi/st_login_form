import streamlit as st
from st_supabase_connection import SupabaseConnection, execute_query

from .auth import _Authenticator


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
    auth = _Authenticator()

    # Select usernames and plaintext passwords from the specified table
    plaintext_passwords = execute_query(
        client.table(user_tablename)
        .select(f"{username_col}, {password_col}")
        .not_.like(password_col, "$argon2id$%")
    ).data

    if len(plaintext_passwords) > 0:
        st.warning(f"Hashing {len(plaintext_passwords)} plaintext passwords.")
        updates = []
        for pair in plaintext_passwords:
            pair["password"] = auth.generate_pwd_hash(pair["password"])
            updates.append({username_col: pair["username"], password_col: pair["password"]})

        client.table(user_tablename).upsert(updates).execute()

        st.success("All passwords hashed successfully.", icon=":material/lock:")
    else:
        st.success("All passwords are already hashed.", icon=":material/lock:")
