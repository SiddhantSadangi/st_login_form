import streamlit as st
from supabase import Client, create_client
import bcrypt

__version__ = "0.3.1"


@st.cache_resource
def init_connection() -> Client:
    try:
        return create_client(
            st.secrets["connections"]["supabase"]["SUPABASE_URL"],
            st.secrets["connections"]["supabase"]["SUPABASE_KEY"],
        )
    except KeyError:
        return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])


def login_success(message: str, username: str) -> None:
    st.success(message)
    st.session_state["authenticated"] = True
    st.session_state["username"] = username


def generate_pwd_hash(password: str):
    """Generates a hashed version of the provided password using bcrypt."""
    # Check if the password is already hashed; if so, return it directly
    if password.startswith("$2b$"):
        return password
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_pwd = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    string_pwd = hashed_pwd.decode("utf8")
    return string_pwd


def verify_password(plain_pwd, hashed_pwd):
    """Verifies if a plaintext password matches a hashed one using bcrypt."""
    # Encode passwords to bytes since bcrypt requires byte inputs for comparison
    pwd_byte_enc = plain_pwd.encode("utf-8")
    hashed_pwd_enc = hashed_pwd.encode("utf-8")
    return bcrypt.checkpw(pwd_byte_enc, hashed_pwd_enc)


def hash_current_passwords(
    user_tablename: str = "users",
    username_col: str = "username",
    password_col: str = "password",
):
    """Hashes all current plaintext passwords stored in a database table (in-place)."""
    # Initialize database connection
    client = init_connection()
    # Select usernames and passwords from the specified table
    user_pass_dicts = (
        client.table(user_tablename)
        .select(f"{username_col}, {password_col}")
        .execute()
        .data
    )

    # Iterate over each username-password pair, re-hash the password, and update the table
    for pair in user_pass_dicts:
        pair["password"] = generate_pwd_hash(pair["password"])
        client.table(user_tablename).update({password_col: pair["password"]}).match(
            {username_col: pair["username"]}
        ).execute()


# Create the python function that will be called
def login_form(
    *,
    title: str = "Authentication",
    user_tablename: str = "users",
    username_col: str = "username",
    password_col: str = "password",
    create_title: str = "Create new account :baby: ",
    login_title: str = "Login to existing account :prince: ",
    allow_guest: bool = True,
    allow_create: bool = True,
    guest_title: str = "Guest login :ninja: ",
    create_username_label: str = "Create a unique username",
    create_username_placeholder: str = None,
    create_username_help: str = None,
    create_password_label: str = "Create a password",
    create_password_placeholder: str = None,
    create_password_help: str = "⚠️ Password will be stored as plain text. Do not reuse from other websites. Password cannot be recovered.",
    create_submit_label: str = "Create account",
    create_success_message: str = "Account created :tada:",
    login_username_label: str = "Enter your unique username",
    login_username_placeholder: str = None,
    login_username_help: str = None,
    login_password_label: str = "Enter your password",
    login_password_placeholder: str = None,
    login_password_help: str = None,
    login_submit_label: str = "Login",
    login_success_message: str = "Login succeeded :tada:",
    login_error_message: str = "Wrong username/password :x: ",
    guest_submit_label: str = "Guest login",
) -> Client:
    """Creates a user login form in Streamlit apps.

    Connects to a Supabase DB using `SUPABASE_URL` and `SUPABASE_KEY` Streamlit secrets.
    Sets `session_state["authenticated"]` to True if the login is successful.
    Sets `session_state["username"]` to provided username or new or existing user, and to `None` for guest login.

    Returns:
    Supabase client instance
    """

    # Initialize supabase connection
    client = init_connection()

    # User Authentication
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if "username" not in st.session_state:
        st.session_state["username"] = None

    with st.expander(title, expanded=not st.session_state["authenticated"]):
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
                    hashed_password = generate_pwd_hash(password)
                    if st.form_submit_button(
                        label=create_submit_label,
                        type="primary",
                        disabled=st.session_state["authenticated"],
                    ):
                        try:
                            client.table(user_tablename).insert(
                                {username_col: username, password_col: hashed_password}
                            ).execute()
                        except Exception as e:
                            st.error(e.message)
                            st.session_state["authenticated"] = False
                        else:
                            login_success(create_success_message, username)

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
                ):
                    response = (
                        client.table(user_tablename)
                        .select(f"{username_col}, {password_col}")
                        .eq(username_col, username)
                        .execute()
                    )
                    if len(response.data) > 0:
                        hashed_password = response.data[0]["password"]
                        if verify_password(password, hashed_password):
                            login_success(login_success_message, username)
                        else:
                            st.error(login_error_message)
                            st.session_state["authenticated"] = False
                    else:
                        st.error(login_error_message)
                        st.session_state["authenticated"] = False

        # Guest login
        if allow_guest:
            with guest_tab:
                if st.button(
                    label=guest_submit_label,
                    type="primary",
                    disabled=st.session_state["authenticated"],
                ):
                    st.session_state["authenticated"] = True

        return client


def main() -> None:
    login_form(
        create_username_placeholder="Username will be visible in the global leaderboard.",
        create_password_placeholder="⚠️ Password will be stored as plain text. You won't be able to recover it if you forget.",
        guest_submit_label="Play as a guest ⚠️ Scores won't be saved",
    )


if __name__ == "__main__":
    main()
