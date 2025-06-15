from typing import Optional

import streamlit as st
from st_supabase_connection import SupabaseConnection

from ._helpers.auth import _Authenticator, _reset_authentication
from ._helpers.forms import (
    CreateAccountConfig,
    FieldConfig,
    GuestLoginConfig,
    LoginFormConfig,
    _get_tabs,
    _handle_create_account,
    _handle_guest_login,
    _handle_login,
)

__version__ = "1.3.1"

__all__ = ["login_form", "hash_current_passwords", "logout"]


def login_form(
    *,
    supabase_connection: Optional[SupabaseConnection] = None,
    title: str = "Authentication",
    icon: str = ":material/lock:",
    user_tablename: str = "users",
    username_col: str = "username",
    password_col: str = "password",
    constrain_password: bool = True,
    create_title: str = ":material/add_circle: Create new account",
    login_title: str = ":material/login: Login to existing account",
    allow_guest: bool = True,
    allow_create: bool = True,
    guest_title: str = ":material/visibility_off: Guest login",
    create_username_label: str = "Create a unique username",
    create_username_placeholder: str = None,
    create_username_help: str = None,
    create_password_label: str = "Create a password",
    create_password_placeholder: str = None,
    create_password_help: str = ":material/warning: Password cannot be recovered if lost",
    create_retype_password_label: str = "Retype password",
    create_retype_password_placeholder: str = None,
    create_retype_password_help: str = None,
    password_constraint_check_fail_message: str = "Password must contain at least 8 characters, including one uppercase letter, one lowercase letter, one number, and one special character (`@$!%*?&_^#- `).",
    password_mismatch_message: str = "Passwords do not match",
    create_submit_label: str = ":material/add_circle: Create account",
    login_username_label: str = "Enter your unique username",
    login_username_placeholder: str = None,
    login_username_help: str = None,
    login_password_label: str = "Enter your password",
    login_password_placeholder: str = None,
    login_password_help: str = None,
    login_submit_label: str = ":material/login: Login",
    login_error_message: str = "Wrong username/password",
    guest_submit_label: str = "Login as guest",
) -> Optional[SupabaseConnection]:
    """
    Creates a user login form in Streamlit apps.

    Connects to a Supabase DB using `SUPABASE_URL` and `SUPABASE_KEY` Streamlit secrets, unless a client is provided.
    Sets `session_state["authenticated"]` to True if the login is successful.
    Sets `session_state["username"]` to provided username or new or existing user, and to `None` for guest login.

    Args:
        supabase_connection (Optional[SupabaseConnection]): An optional Supabase connection instance. If not provided, one will be created.
        title (str): The title of the login form. Default is "Authentication".
        icon (str): The icon to display next to the title. Default is ":material/lock:".
        user_tablename (str): The name of the table in the database that stores user information. Default is "users".
        username_col (str): The name of the column in the user table that stores usernames. Default is "username".
        password_col (str): The name of the column in the user table that stores passwords. Default is "password".
        constrain_password (bool): Whether to enforce password constraints (at least 8 characters, including one uppercase letter, one lowercase letter, one number, and one special character (`@$!%*?&_^#- `)). Default is True.
        create_title (str): The title of the create new account tab. Default is ":material/add_circle: Create new account".
        login_title (str): The title of the login to existing account tab. Default is ":material/login: Login to existing account".
        allow_guest (bool): Whether to allow guest login. Default is True.
        allow_create (bool): Whether to allow creating new accounts. Default is True.
        guest_title (str): The title of the guest login tab. Default is ":material/visibility_off: Guest login".
        create_username_label (str): The label for the create username input field. Default is "Create a unique username".
        create_username_placeholder (str): The placeholder text for the create username input field. Default is None.
        create_username_help (str): The help text for the create username input field. Default is None.
        create_password_label (str): The label for the create password input field. Default is "Create a password".
        create_password_placeholder (str): The placeholder text for the create password input field. Default is None.
        create_password_help (str): The help text for the create password input field. Default is ":material/warning: Password cannot be recovered if lost".
        create_retype_password_label (str): The label for the create retype password input field. Default is "Retype password".
        create_retype_password_placeholder (str): The placeholder text for the create retype password input field. Default is None.
        create_retype_password_help (str): The help text for the create retype password input field. Default is None.
        create_submit_label (str): The label for the create account submit button. Default is ":material/add_circle: Create account".
        password_constraint_check_fail_message (str): The error message displayed when the password does not meet the constraints. Default is "Password must contain at least 8 characters, including one uppercase letter, one lowercase letter, one number, and one special character (`@$!%*?&_^#- `).".
        password_mismatch_message (str): The error message displayed when the passwords do not match. Default is "Passwords do not match".
        login_username_label (str): The label for the login username input field. Default is "Enter your unique username".
        login_username_placeholder (str): The placeholder text for the login username input field. Default is None.
        login_username_help (str): The help text for the login username input field. Default is None.
        login_password_label (str): The label for the login password input field. Default is "Enter your password".
        login_password_placeholder (str): The placeholder text for the login password input field. Default is None.
        login_password_help (str): The help text for the login password input field. Default is None.
        login_submit_label (str): The label for the login submit button. Default is ":material/login: Login".
        login_error_message (str): The error message displayed when the username or password is incorrect. Default is "Wrong username/password".
        guest_submit_label (str): The label for the guest login button. Default is "Login as guest".
    Returns:
        Optional[SupabaseConnection]: The Supabase connection instance for performing downstream Supabase operations, or `None` if the user is not authenticated.

    Example:
    >>> supabase_connection = st_login_form.login_form()

    >>> if st.session_state["authenticated"]:
    >>>     if st.session_state["username"]:
    >>>         st.success(f"Welcome {st.session_state['username']}")
    >>>     else:
    >>>         st.success("Welcome guest")
    >>> else:
    >>>     st.error("Not authenticated")
    """

    if supabase_connection is None:
        supabase_connection = st.connection(name="supabase", type=SupabaseConnection)
    elif not isinstance(supabase_connection, SupabaseConnection):
        st.error(
            "`supabase_connection` must be a [`SupabaseConnection`](https://github.com/SiddhantSadangi/st_supabase_connection) instance",
            icon=":material/warning:",
        )
        st.stop()

    auth = _Authenticator()

    # User Authentication
    if "authenticated" not in st.session_state:
        _reset_authentication()

    if "username" not in st.session_state:
        st.session_state["username"] = None

    if not st.session_state["authenticated"]:
        with st.expander(title, icon=icon, expanded=True):
            create_tab, login_tab, guest_tab = _get_tabs(
                allow_create, allow_guest, create_title, login_title, guest_title
            )

            # Create new account
            if allow_create:
                with create_tab:
                    create_cfg = CreateAccountConfig(
                        username=FieldConfig(
                            label=create_username_label,
                            placeholder=create_username_placeholder,
                            help=create_username_help,
                        ),
                        password=FieldConfig(
                            label=create_password_label,
                            placeholder=create_password_placeholder,
                            help=create_password_help,
                        ),
                        submit_label=create_submit_label,
                        constrain_password=constrain_password,
                        password_fail_message=password_constraint_check_fail_message,
                        create_retype_password_label=create_retype_password_label,
                        create_retype_password_placeholder=create_retype_password_placeholder,
                        create_retype_password_help=create_retype_password_help,
                        password_mismatch_message=password_mismatch_message,
                    )
                    _handle_create_account(
                        auth=auth,
                        client=supabase_connection.client,
                        user_tablename=user_tablename,
                        username_col=username_col,
                        password_col=password_col,
                        cfg=create_cfg,
                    )

            # Login to existing account
            with login_tab:
                login_cfg = LoginFormConfig(
                    username=FieldConfig(
                        label=login_username_label,
                        placeholder=login_username_placeholder,
                        help=login_username_help,
                    ),
                    password=FieldConfig(
                        label=login_password_label,
                        placeholder=login_password_placeholder,
                        help=login_password_help,
                    ),
                    submit_label=login_submit_label,
                    error_message=login_error_message,
                )
                _handle_login(
                    auth=auth,
                    client=supabase_connection.client,
                    user_tablename=user_tablename,
                    username_col=username_col,
                    password_col=password_col,
                    cfg=login_cfg,
                )

            # Guest login
            if allow_guest:
                with guest_tab:
                    guest_cfg = GuestLoginConfig(submit_label=guest_submit_label)
                    _handle_guest_login(cfg=guest_cfg)
    elif st.button("Logout", icon=":material/logout:", use_container_width=True):
        logout()

    return supabase_connection if st.session_state["authenticated"] else None


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
    from st_supabase_connection import execute_query

    # Initialize the Supabase connection
    supabase_connection = st.connection(name="supabase", type=SupabaseConnection)
    auth = _Authenticator()

    # Select usernames and plaintext passwords from the specified table
    plaintext_passwords = execute_query(
        supabase_connection.table(user_tablename)
        .select(f"{username_col}, {password_col}")
        .not_.like(password_col, "$argon2id$%")
    ).data

    if len(plaintext_passwords) > 0:
        st.warning(f"Hashing {len(plaintext_passwords)} plaintext passwords.")
        updates = []
        for pair in plaintext_passwords:
            pair[password_col] = auth.generate_pwd_hash(pair[password_col])
            updates.append({username_col: pair[username_col], password_col: pair[password_col]})

        supabase_connection.table(user_tablename).upsert(
            updates, on_conflict=username_col
        ).execute()

        st.success("All passwords hashed successfully.", icon=":material/lock:")
    else:
        st.success("All passwords are already hashed.", icon=":material/lock:")


def logout() -> None:
    """
    Logs out the current user by resetting authentication state.
    """
    _reset_authentication()
    st.rerun()


if __name__ == "__main__":
    login_form()
