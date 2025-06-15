from dataclasses import dataclass

import streamlit as st

from .auth import _reset_authentication, _set_authenticated, _validate_password


@dataclass
class FieldConfig:
    label: str
    placeholder: str = None
    help: str = None
    type: str = "text"


@dataclass
class CreateAccountConfig:
    username: FieldConfig
    password: FieldConfig
    submit_label: str
    constrain_password: bool
    password_fail_message: str
    create_retype_password_label: str
    create_retype_password_placeholder: str
    create_retype_password_help: str


@dataclass
class LoginFormConfig:
    username: FieldConfig
    password: FieldConfig
    submit_label: str
    error_message: str


@dataclass
class GuestLoginConfig:
    submit_label: str


def _get_tabs(allow_create, allow_guest, create_title, login_title, guest_title):
    # 1) collect only the enabled actions
    options = []
    if allow_create:
        options.append(("create", create_title))
    options.append(("login", login_title))
    if allow_guest:
        options.append(("guest", guest_title))

    # 2) early exit if there's only one pane
    if len(options) <= 1:
        return None, st.container(), None

    # 3) render and zip into a dict
    keys, titles = zip(*options)
    tabs = dict(zip(keys, st.tabs(titles)))

    # 4) return in fixed order
    return tabs.get("create"), tabs["login"], tabs.get("guest")


def _render_input(field: FieldConfig, disabled: bool):
    kwargs = {
        "label": field.label,
        "placeholder": field.placeholder,
        "help": field.help,
        "disabled": disabled,
    }
    if field.type != "text":
        kwargs["type"] = field.type
    return st.text_input(**kwargs)


def _handle_create_account(
    auth,
    client,
    user_tablename,
    username_col,
    password_col,
    cfg: CreateAccountConfig,
):
    with st.form(key="create"):
        username = _render_input(cfg.username, disabled=st.session_state["authenticated"])
        password_field = FieldConfig(**{**cfg.password.__dict__, "type": "password"})
        password = _render_input(password_field, disabled=st.session_state["authenticated"])
        retype_password_field = FieldConfig(
            **{
                **password_field.__dict__,
                "type": "password",
                "label": cfg.create_retype_password_label,
                "placeholder": cfg.create_retype_password_placeholder,
                "help": cfg.create_retype_password_help,
            }
        )
        retype_password = _render_input(
            retype_password_field, disabled=st.session_state["authenticated"]
        )

        if st.form_submit_button(
            label=cfg.submit_label,
            type="primary",
            disabled=st.session_state["authenticated"],
            use_container_width=True,
        ):
            if password != retype_password:
                st.error("Passwords do not match", icon=":material/warning:")
                st.stop()

            if cfg.constrain_password and not _validate_password(password):
                st.error(cfg.password_fail_message)
                st.stop()

            try:
                hashed_password = auth.generate_pwd_hash(password)
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
    cfg: LoginFormConfig,
):
    with st.form(key="login"):
        username = _render_input(cfg.username, disabled=st.session_state["authenticated"])
        password_field = FieldConfig(**{**cfg.password.__dict__, "type": "password"})
        password = _render_input(password_field, disabled=st.session_state["authenticated"])

        if st.form_submit_button(
            label=cfg.submit_label,
            disabled=st.session_state["authenticated"],
            type="primary",
            use_container_width=True,
        ):
            try:
                response = (
                    client.table(user_tablename)
                    .select(f"{username_col}, {password_col}")
                    .eq(username_col, username)
                    .execute()
                )
            except Exception as e:
                st.error(str(e))
                _reset_authentication()
            else:
                if len(response.data) > 0:
                    db_password = response.data[0][password_col]

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
                        st.error(cfg.error_message)
                        _reset_authentication()

                else:
                    st.error(cfg.error_message)
                    _reset_authentication()


def _handle_guest_login(cfg: GuestLoginConfig):
    if st.button(
        label=cfg.submit_label,
        type="primary",
        disabled=st.session_state["authenticated"],
        use_container_width=True,
    ):
        _set_authenticated()
        st.rerun()
