import argon2
import streamlit as st
from streamlit.connections import SQLConnection
from st_supabase_connection import SupabaseConnection
from stqdm import stqdm
from supabase import Client
from sqlalchemy import text
from sqlalchemy.sql.elements import quoted_name

__version__ = "1.3.0"


def validate_password(
    password: str, min_length: int = 8, special_chars: str = "@$!%*?&_^#- "
) -> bool:
    required_chars = [
        lambda s: any(x.isupper() for x in s),
        lambda s: any(x.islower() for x in s),
        lambda s: any(x.isdigit() for x in s),
        lambda s: any(x in special_chars for x in s),
    ]
    return len(password) >= min_length and all(
        check(password) for check in required_chars
    )


def login_success(username: str, role: str | None = None) -> None:
    st.session_state["authenticated"] = True
    st.session_state["username"] = username
    if role is not None:
        st.session_state["authenticated_role"] = role.lower()


class Authenticator(argon2.PasswordHasher):
    """A class derived from `argon2.PasswordHasher` to provide functionality for the authentication process"""

    def generate_pwd_hash(self, password: str):
        """Generates a hashed version of the provided password using `argon2`."""
        return password if password.startswith("$argon2id$") else self.hash(password)

    def verify_password(self, hashed_password, plain_password):
        """Verifies if a plaintext password matches a hashed one using `argon2`."""
        try:
            if self.verify(hashed_password, plain_password):
                return True
        except argon2.exceptions.VerificationError:
            return False


# Create the python function that will be called
def login_form(
    *,
    connection: SQLConnection | SupabaseConnection | None = None,
    title: str = "Authentication",
    icon: str = ":material/lock:",
    user_databasename: str = None,
    user_schemaname: str = None,
    user_tablename: str = "users",
    username_col: str = "username",
    password_col: str = "password",
    retrieve_role: bool = False,
    role_col: str = "role",
    role_default: str = "user",
    constrain_password: bool = True,
    create_title: str = ":material/add_circle: Create new account",
    login_title: str = ":material/login: Login to existing account",
    guest_title: str = ":material/visibility_off: Guest login",
    allow_guest: bool = True,
    allow_create: bool = True,
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
    """Creates a user login form in Streamlit apps.

    Connects to a database using either a provided connection or creates a new Supabase connection
    using `SUPABASE_URL` and `SUPABASE_KEY` Streamlit secrets.
    Sets `session_state["authenticated"]` to True if the login is successful.
    Sets `session_state["username"]` to provided username or new or existing user, and to `None` for guest login.

    Arguments:
        connection: Optional pre-configured connection instance. If not provided, creates a Supabase connection.
        title (str): The title of the login form. Default is "Authentication".
        icon (str): The icon to display next to the title. Default is ":material/lock:".
        user_databasename (str): The name of the database that stores user information. Default is None.
        user_schemaname (str): The name of the schema that stores user information. Default is None.
        user_tablename (str): The name of the table in the database that stores user information. Default is "users".
        username_col (str): The name of the column in the user table that stores usernames. Default is "username".
        password_col (str): The name of the column in the user table that stores passwords. Default is "password".
        retrieve_role (bool): Whether to retrieve the role of the user. Default is False.
        role_col (str): The name of the column in the user table that stores roles. Default is "role".
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
        create_submit_label (str): The label for the create account submit button. Default is ":material/add_circle: Create account".
        login_username_label (str): The label for the login username input field. Default is "Enter your unique username".
        login_username_placeholder (str): The placeholder text for the login username input field. Default is None.
        login_username_help (str): The help text for the login username input field. Default is None.
        login_password_label (str): The label for the login password input field. Default is "Enter your password".
        login_password_placeholder (str): The placeholder text for the login password input field. Default is None.
        login_password_help (str): The help text for the login password input field. Default is None.
        login_submit_label (str): The label for the login submit button. Default is ":material/login: Login".
        login_error_message (str): The error message displayed when the username or password is incorrect. Default is ":material/lock: Wrong username/password".
        password_constraint_check_fail_message (str): The error message displayed when the password does not meet the constraints. Default is ":material/warning: Password must contain at least 8 characters, including one uppercase letter, one lowercase letter, one number, and one special character (`@$!%*?&_^#- `).".
        guest_submit_label (str): The label for the guest login button. Default is ":material/visibility_off: Guest login".

    Returns:
        Connection.client: The client instance for performing downstream database (e.g., SQL, Supabase) operations.

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

    # Initialize the connection
    client = (
        connection
        if connection is not None
        else st.connection(name="supabase", type=SupabaseConnection)
    )
    auth = Authenticator()

    def get_fully_qualified_name(connection, database, schema, table):
        """Helper function to generate fully qualified table name based on connection type."""
        # Quote each identifier separately
        table = quoted_name(table, True)
        engine_str = str(connection.engine)

        if engine_str.startswith("Engine(postgres"):
            schema = quoted_name(schema or "public", True)
            database = quoted_name(database or "postgres", True)
            return f"{database}.{schema}.{table}"
        elif engine_str.startswith("Engine(mysql"):
            database = quoted_name(database or "mysql", True)
            return f"{database}.{table}"
        elif engine_str.startswith("Engine(sqlite"):
            return str(table)
        raise ValueError(f"This SQLAlchemy engine is not yet supported: {engine_str}")

    def execute_update(connection, fqn, password_col, username_col, password, username):
        """Helper function to execute update statement across different database engines."""
        # Use parameterized query with quoted column names
        password_col = quoted_name(password_col, True)
        username_col = quoted_name(username_col, True)

        with connection.session as session:
            query = text(
                f"UPDATE {fqn} SET {password_col} = :pwd WHERE {username_col} = :user"
            )
            session.execute(query, {"pwd": password, "user": username})
            session.commit()

    def rehash_pwd_in_db(password, username) -> str:
        """A procedure to rehash given password in the db if necessary."""
        hashed_password = auth.generate_pwd_hash(password)

        if isinstance(connection, SQLConnection):
            fqn = get_fully_qualified_name(
                connection, user_databasename, user_schemaname, user_tablename
            )
            execute_update(
                connection, fqn, password_col, username_col, hashed_password, username
            )
        else:
            client.table(user_tablename).update({password_col: hashed_password}).match(
                {username_col: username}
            ).execute()

        return hashed_password

    # User Authentication
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if "authenticated_role" not in st.session_state:
        st.session_state["authenticated_role"] = None

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
                            if isinstance(client, SQLConnection):
                                fqn = get_fully_qualified_name(
                                    client,
                                    user_databasename,
                                    user_schemaname,
                                    user_tablename,
                                )
                                username_col_quoted = quoted_name(username_col, True)
                                password_col_quoted = quoted_name(password_col, True)

                                # Include role in INSERT if role retrieval is enabled
                                cols = f"{username_col_quoted}, {password_col_quoted}"
                                values = f":username, :password"
                                if retrieve_role:
                                    role_col_quoted = quoted_name(role_col, True)
                                    cols += f", {role_col_quoted}"
                                    values += ", :role"
                                    # Normalize role_default to lowercase when creating user
                                    params["role"] = role_default.lower()

                                query = text(
                                    f"INSERT INTO {fqn} ({cols}) " f"VALUES ({values})"
                                )
                                with client.session as session:
                                    session.execute(
                                        query,
                                        {
                                            "username": username,
                                            "password": hashed_password,
                                            **(
                                                {"role": role_default.lower()}
                                                if retrieve_role
                                                else {}
                                            ),
                                        },
                                    )
                                    session.commit()
                            else:
                                # Supabase client
                                insert_data = {
                                    username_col: username,
                                    password_col: hashed_password,
                                }
                                if retrieve_role:
                                    insert_data[role_col] = role_default.lower()

                                client.table(user_tablename).insert(
                                    insert_data
                                ).execute()
                        except Exception as e:
                            error_message = getattr(
                                e, "message", str(e)
                            )  # Fallback to str(e) if no message attribute
                            st.error(error_message)
                            st.session_state["authenticated"] = False
                        else:
                            login_success(username)
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
                    if isinstance(client, SQLConnection):
                        fqn = get_fully_qualified_name(
                            client, user_databasename, user_schemaname, user_tablename
                        )
                        username_col_quoted = quoted_name(username_col, True)
                        password_col_quoted = quoted_name(password_col, True)

                        # Add role to SELECT if needed
                        select_cols = f"{username_col_quoted}, {password_col_quoted}"
                        if retrieve_role:
                            role_col_quoted = quoted_name(role_col, True)
                            select_cols += f", {role_col_quoted}"

                        query = text(
                            f"SELECT {select_cols} "
                            f"FROM {fqn} WHERE {username_col_quoted} = :username"
                        )
                        with client.session as session:
                            result = session.execute(query, {"username": username})
                            # Include role in dictionary if it was retrieved
                            data = [
                                {
                                    username_col: row[0],
                                    password_col: row[1],
                                    **({"role": row[2]} if retrieve_role else {}),
                                }
                                for row in result
                            ]
                    else:
                        # Supabase client
                        select_cols = f"{username_col}, {password_col}"
                        if retrieve_role:
                            select_cols += f", {role_col}"

                        response = (
                            client.table(user_tablename)
                            .select(select_cols)
                            .eq(username_col, username)
                            .execute()
                        )
                        data = response.data

                    if len(data) > 0:
                        db_password = data[0][password_col]

                        if not db_password.startswith("$argon2id$"):
                            db_password = rehash_pwd_in_db(db_password, username)

                        if auth.verify_password(db_password, password):
                            # Normalize role to lowercase if it exists
                            role = (
                                data[0].get("role", "").lower()
                                if retrieve_role
                                else None
                            )
                            login_success(username, role)

                            if auth.check_needs_rehash(db_password):
                                _ = rehash_pwd_in_db(password, username)
                            st.rerun()
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
                    use_container_width=True,
                ):
                    st.session_state["authenticated"] = True
                    st.session_state["username"] = None
                    st.session_state["authenticated_role"] = "guest"
                    st.rerun()
        return client


def hash_current_passwords(
    connection: SQLConnection | SupabaseConnection | None = None,
    user_databasename: str = None,
    user_schemaname: str = None,
    user_tablename: str = "users",
    username_col: str = "username",
    password_col: str = "password",
) -> None:
    """Hashes all current plaintext passwords stored in a database table (in-place)."""

    # Initialize the connection
    client = (
        connection
        if connection is not None
        else st.connection(name="supabase", type=SupabaseConnection)
    )
    auth = Authenticator()

    # Select usernames and plaintext passwords based on connection type
    if isinstance(client, SQLConnection):
        fqn = get_fully_qualified_name(
            client, user_databasename, user_schemaname, user_tablename
        )
        username_col_quoted = quoted_name(username_col, True)
        password_col_quoted = quoted_name(password_col, True)

        query = text(
            f"SELECT {username_col_quoted}, {password_col_quoted} FROM {fqn} "
            f"WHERE {password_col_quoted} NOT LIKE :pattern"
        )

        with client.session as session:
            result = session.execute(query, {"pattern": "$argon2id$%"})
            user_pass_dicts = [
                {username_col: row[0], password_col: row[1]} for row in result
            ]
    else:  # Supabase
        from st_supabase_connection import execute_query

        user_pass_dicts = execute_query(
            client.table(user_tablename)
            .select(f"{username_col}, {password_col}")
            .not_.like(password_col, "$argon2id$%")
        ).data

    if len(user_pass_dicts) > 0:
        st.warning(f"Hashing {len(user_pass_dicts)} plaintext passwords.")
        for pair in stqdm(user_pass_dicts):
            pair["password"] = auth.generate_pwd_hash(pair["password"])
            if isinstance(client, SQLConnection):
                fqn = get_fully_qualified_name(
                    client, user_databasename, user_schemaname, user_tablename
                )
                execute_update(
                    client,
                    fqn,
                    password_col,
                    username_col,
                    pair["password"],
                    pair["username"],
                )
            else:
                client.table(user_tablename).update(
                    {password_col: pair["password"]}
                ).match({username_col: pair["username"]}).execute()
        st.success("All passwords hashed successfully.", icon="🔒")
    else:
        st.success("All passwords are already hashed.", icon="🔒")


if __name__ == "__main__":
    login_form()
