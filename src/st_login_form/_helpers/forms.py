import streamlit as st

from .auth import _reset_authentication, _set_authenticated, _validate_password


def _get_tabs(allow_create, allow_guest, create_title, login_title, guest_title):
    tab_titles = []
    if allow_create:
        tab_titles.append(create_title)
    tab_titles.append(login_title)
    if allow_guest:
        tab_titles.append(guest_title)
    if len(tab_titles) <= 1:
        return None, st.container(), None
    tabs = st.tabs(tab_titles)
    idx = 0
    if allow_create:
        create_tab = tabs[idx]
        idx += 1
    login_tab = tabs[idx]
    idx += 1
    guest_tab = tabs[idx] if allow_guest else None
    return create_tab if allow_create else None, login_tab, guest_tab


def _handle_create_account(
    auth,
    client,
    user_tablename,
    username_col,
    password_col,
    create_username_label,
    create_username_placeholder,
    create_username_help,
    create_password_label,
    create_password_placeholder,
    create_password_help,
    create_submit_label,
    constrain_password,
    password_constraint_check_fail_message,
):
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
            if constrain_password and not _validate_password(password):
                st.error(password_constraint_check_fail_message)
                st.stop()

            try:
                client.table(user_tablename).insert(
                    {username_col: username, password_col: hashed_password}
                ).execute()
            except Exception as e:
                st.error(str(e))
                _reset_authentication()
            else:
                _set_authenticated(username)
                st.rerun()


def _handle_login(
    auth,
    client,
    user_tablename,
    username_col,
    password_col,
    login_username_label,
    login_username_placeholder,
    login_username_help,
    login_password_label,
    login_password_placeholder,
    login_password_help,
    login_submit_label,
    login_error_message,
):
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
                    db_password = auth.rehash_pwd_in_db(
                        password=db_password,
                        username=username,
                        client=client,
                        user_tablename=user_tablename,
                        password_col=password_col,
                        username_col=username_col,
                    )

                if auth.verify_password(db_password, password):
                    # Verify hashed password
                    _set_authenticated(username)
                    # This step is recommended by the argon2-cffi documentation
                    if auth.check_needs_rehash(db_password):
                        _ = auth.rehash_pwd_in_db(
                            password=password,
                            username=username,
                            client=client,
                            user_tablename=user_tablename,
                            password_col=password_col,
                            username_col=username_col,
                        )
                    st.rerun()
                else:
                    st.error(login_error_message)
                    _reset_authentication()

            else:
                st.error(login_error_message)
                _reset_authentication()


def _handle_guest_login(
    guest_submit_label,
):
    if st.button(
        label=guest_submit_label,
        type="primary",
        disabled=st.session_state["authenticated"],
        use_container_width=True,
    ):
        _set_authenticated()
        st.rerun()
