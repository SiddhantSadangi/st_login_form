from typing import Optional

import streamlit as st
from st_supabase_connection import SupabaseConnection
from supabase import Client

from .auth import (
    Authenticator,
    reset_authentication,
    set_authenticated,
    validate_password,
)

__version__ = "1.3.0"


def login_form(
    *,
    client: Optional[Client] = None,
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
    create_submit_label: str = ":material/add_circle: Create account",
    login_username_label: str = "Enter your unique username",
    login_username_placeholder: str = None,
    login_username_help: str = None,
    login_password_label: str = "Enter your password",
    login_password_placeholder: str = None,
    login_password_help: str = None,
    login_submit_label: str = ":material/login: Login",
    login_error_message: str = ":material/lock: Wrong username/password",
    password_constraint_check_fail_message: str = ":material/warning: Password must contain at least 8 characters, including one uppercase letter, one lowercase letter, one number, and one special character (`@$!%*?&_^#- `).",
    guest_submit_label: str = ":material/visibility_off: Guest login",
) -> Client:
    """
    Creates a user login form in Streamlit apps.

    Connects to a Supabase DB using `SUPABASE_URL` and `SUPABASE_KEY` Streamlit secrets, unless a client is provided.
    Sets `session_state["authenticated"]` to True if the login is successful.
    Sets `session_state["username"]` to provided username or new or existing user, and to `None` for guest login.

    Args:
        client (Optional[Client]): An optional Supabase client instance. If not provided, one will be created.
        title (str): The title of the login form.
        icon (str): The icon to display next to the title.
        user_tablename (str): The name of the table in the database that stores user information.
        username_col (str): The name of the column in the user table that stores usernames.
        password_col (str): The name of the column in the user table that stores passwords.
        constrain_password (bool): Whether to enforce password constraints.
        create_title (str): The title of the create new account tab.
        login_title (str): The title of the login to existing account tab.
        allow_guest (bool): Whether to allow guest login.
        allow_create (bool): Whether to allow creating new accounts.
        guest_title (str): The title of the guest login tab.
        create_username_label (str): The label for the create username input field.
        create_username_placeholder (str): The placeholder text for the create username input field.
        create_username_help (str): The help text for the create username input field.
        create_password_label (str): The label for the create password input field.
        create_password_placeholder (str): The placeholder text for the create password input field.
        create_password_help (str): The help text for the create password input field.
        create_submit_label (str): The label for the create account submit button.
        login_username_label (str): The label for the login username input field.
        login_username_placeholder (str): The placeholder text for the login username input field.
        login_username_help (str): The help text for the login username input field.
        login_password_label (str): The label for the login password input field.
        login_password_placeholder (str): The placeholder text for the login password input field.
        login_password_help (str): The help text for the login password input field.
        login_submit_label (str): The label for the login submit button.
        login_error_message (str): The error message displayed when the username or password is incorrect.
        password_constraint_check_fail_message (str): The error message displayed when the password does not meet the constraints.
        guest_submit_label (str): The label for the guest login button.

    Returns:
        Client: The Supabase client instance for performing downstream supabase operations.

    Example:
    >>> client = st_login_form.login_form(user_tablename="demo_users")

    >>> if st.session_state["authenticated"]:
    >>>     if st.session_state["username"]:
    >>>         st.success(f"Welcome {st.session_state['username']}")
    >>>     else:
    >>>         st.success("Welcome guest")
    >>> else:
    >>>     st.error("Not authenticated")
    """

    if client is None:
        client = st.connection(name="supabase", type=SupabaseConnection)
    auth = Authenticator()

    def rehash_pwd_in_db(password, username) -> str:
        """A procedure to rehash given password in the db if necessary."""
        hashed_password = auth.generate_pwd_hash(password)
        client.table(user_tablename).update({password_col: hashed_password}).match(
            {username_col: username}
        ).execute()

        return hashed_password

    # User Authentication
    if "authenticated" not in st.session_state:
        reset_authentication()

    if "username" not in st.session_state:
        st.session_state["username"] = None

    with st.expander(title, icon=icon, expanded=not st.session_state["authenticated"]):
        if allow_guest:
            if allow_create:
                create_tab, login_tab, guest_tab = st.tabs(
                    [
                        create_title,
                        login_title,
                        guest_title,
                    ]
                )
            else:
                login_tab, guest_tab = st.tabs([login_title, guest_title])
        elif allow_create:
            create_tab, login_tab = st.tabs(
                [
                    create_title,
                    login_title,
                ]
            )
        else:
            login_tab = st.container()

        # Create new account
        if allow_create:
            with create_tab:
                with st.form(key="create"):
                    username = st.text_input(
                        label=create_username_label,
                        placeholder=create_username_placeholder,
                        help=create_username_help,
                        disabled=st.session_state["authenticated"],
                    )

                    password = st.text_input(
                        label=create_password_label,
                        placeholder=create_password_placeholder,
                        help=create_password_help,
                        type="password",
                        disabled=st.session_state["authenticated"],
                    )
                    hashed_password = auth.generate_pwd_hash(password)
                    if st.form_submit_button(
                        label=create_submit_label,
                        type="primary",
                        disabled=st.session_state["authenticated"],
                        use_container_width=True,
                    ):
                        if constrain_password and not validate_password(password):
                            st.error(password_constraint_check_fail_message)
                            st.stop()

                        try:
                            client.table(user_tablename).insert(
                                {username_col: username, password_col: hashed_password}
                            ).execute()
                        except Exception as e:
                            st.error(str(e))
                            reset_authentication()
                        else:
                            set_authenticated(username)
                            st.rerun()

        # Login to existing account
        with login_tab:
            with st.form(key="login"):
                username = st.text_input(
                    label=login_username_label,
                    placeholder=login_username_placeholder,
                    help=login_username_help,
                    disabled=st.session_state["authenticated"],
                )

                password = st.text_input(
                    label=login_password_label,
                    placeholder=login_password_placeholder,
                    help=login_password_help,
                    type="password",
                    disabled=st.session_state["authenticated"],
                )

                if st.form_submit_button(
                    label=login_submit_label,
                    disabled=st.session_state["authenticated"],
                    type="primary",
                    use_container_width=True,
                ):
                    response = (
                        client.table(user_tablename)
                        .select(f"{username_col}, {password_col}")
                        .eq(username_col, username)
                        .execute()
                    )

                    if len(response.data) > 0:
                        db_password = response.data[0]["password"]

                        if not db_password.startswith("$argon2id$"):
                            # Hash plaintext password and update the db
                            db_password = rehash_pwd_in_db(db_password, username)

                        if auth.verify_password(db_password, password):
                            # Verify hashed password
                            set_authenticated(username)
                            # This step is recommended by the argon2-cffi documentation
                            if auth.check_needs_rehash(db_password):
                                _ = rehash_pwd_in_db(password, username)
                            st.rerun()
                        else:
                            st.error(login_error_message)
                            reset_authentication()

                    else:
                        st.error(login_error_message)
                        reset_authentication()

        # Guest login
        if allow_guest:
            with guest_tab:
                if st.button(
                    label=guest_submit_label,
                    type="primary",
                    disabled=st.session_state["authenticated"],
                    use_container_width=True,
                ):
                    set_authenticated()
                    st.rerun()
        return client


if __name__ == "__main__":
    login_form()
