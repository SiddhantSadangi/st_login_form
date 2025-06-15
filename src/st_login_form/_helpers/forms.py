import dataclasses
from typing import Optional

import streamlit as st

from .auth import _reset_authentication, _set_authenticated, _validate_password


@dataclasses.dataclass
class FieldConfig:
    label: str
    placeholder: Optional[str] = None
    help: Optional[str] = None
    type: str = "text"


@dataclasses.dataclass
class CreateAccountConfig:
    username: FieldConfig
    password: FieldConfig
    submit_label: str
    constrain_password: bool
    password_fail_message: Optional[str] = None
    create_retype_password_label: Optional[str] = None
    create_retype_password_placeholder: Optional[str] = None
    create_retype_password_help: Optional[str] = None
    password_mismatch_message: Optional[str] = None


@dataclasses.dataclass
class LoginFormConfig:
    username: FieldConfig
    password: FieldConfig
    submit_label: str
    error_message: str


@dataclasses.dataclass
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


def _submit_form(
    form_key: str,
    fields: dict[str, FieldConfig],
    submit_label: str,
    disabled: bool,
) -> tuple[bool, dict[str, str]]:
    """Renders a Streamlit form for the given fields, returns (submitted, values)."""
    with st.form(key=form_key):
        values = {name: _render_input(field, disabled) for name, field in fields.items()}
        submitted = st.form_submit_button(
            label=submit_label,
            type="primary",
            disabled=disabled,
            use_container_width=True,
        )
    return submitted, values


def _get_validated_inputs(
    form_key: str,
    fields: dict[str, FieldConfig],
    submit_label: str,
    disabled: bool,
) -> Optional[dict[str, str]]:
    submitted, inputs = _submit_form(form_key, fields, submit_label, disabled)
    if not submitted:
        return None
    if missing := [name for name, val in inputs.items() if not val]:
        st.error(f"Please fill in all fields: {', '.join(missing)}", icon=":material/warning:")
        st.stop()
    return inputs


def _handle_create_account(
    auth,
    client,
    user_tablename,
    username_col,
    password_col,
    cfg: CreateAccountConfig,
):
    disabled = st.session_state["authenticated"]
    fields = {
        "username": cfg.username,
        "password": dataclasses.replace(cfg.password, type="password"),
        "retype": dataclasses.replace(
            cfg.password,
            type="password",
            label=cfg.create_retype_password_label,
            placeholder=cfg.create_retype_password_placeholder,
            help=cfg.create_retype_password_help,
        ),
    }

    inputs = _get_validated_inputs("create", fields, cfg.submit_label, disabled)
    if inputs is None:
        return

    username, password, retype = inputs["username"], inputs["password"], inputs["retype"]
    if password != retype:
        st.error(cfg.password_mismatch_message, icon=":material/warning:")
        st.stop()
    if cfg.constrain_password and not _validate_password(password):
        st.error(cfg.password_fail_message, icon=":material/warning:")
        st.stop()
    try:
        hashed = auth.generate_pwd_hash(password)
        client.table(user_tablename).insert(
            {username_col: username, password_col: hashed}
        ).execute()
    except Exception as e:
        st.error(str(e), icon=":material/warning:")
        _reset_authentication()
        st.stop()
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
    disabled = st.session_state["authenticated"]
    fields = {
        "username": cfg.username,
        "password": dataclasses.replace(cfg.password, type="password"),
    }

    inputs = _get_validated_inputs("login", fields, cfg.submit_label, disabled)
    if inputs is None:
        return

    username, password = inputs["username"], inputs["password"]
    try:
        resp = (
            client.table(user_tablename)
            .select(f"{username_col}, {password_col}")
            .eq(username_col, username)
            .execute()
        )
    except Exception as e:
        st.error(str(e), icon=":material/warning:")
        _reset_authentication()
        return

    if not resp.data:
        st.error(cfg.error_message, icon=":material/warning:")
        _reset_authentication()
        return

    db_password = resp.data[0][password_col]
    if not db_password.startswith("$argon2id$"):
        db_password = auth.rehash_pwd_in_db(
            password=db_password,
            username=username,
            client=client,
            user_tablename=user_tablename,
            password_col=password_col,
            username_col=username_col,
        )

    if not auth.verify_password(db_password, password):
        st.error(cfg.error_message, icon=":material/warning:")
        _reset_authentication()
        return

    _set_authenticated(username)
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


def _handle_guest_login(cfg: GuestLoginConfig):
    if st.button(
        label=cfg.submit_label,
        type="primary",
        icon=":material/visibility_off:",
        disabled=st.session_state["authenticated"],
        use_container_width=True,
    ):
        _set_authenticated()
        st.rerun()
