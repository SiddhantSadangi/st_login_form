import streamlit as st

import st_login_form

VERSION = st_login_form.__version__

st.set_page_config(
    page_title="Streamlit Login Form",
    page_icon="🔐",
    menu_items={
        "About": f"Streamlit Login Form 🔐 v{VERSION}  "
        f"\nApp contact: [Siddhant Sadangi](mailto:siddhant.sadangi@gmail.com)",
        "Report a Bug": "https://github.com/SiddhantSadangi/st-login-form/issues/new",
        "Get help": None,
    },
)

# ---------- SIDEBAR ----------
with open("assets/sidebar.html", "r", encoding="UTF-8") as sidebar_file:
    sidebar_html = sidebar_file.read().replace("{VERSION}", VERSION)

with st.sidebar:
    st.components.v1.html(sidebar_html, height=600)

# ---------- MAIN PAGE ----------
st.title("🔐 [`st-login-form`](https://github.com/SiddhantSadangi/st_login_form) demo app ")

st.write(
    "This app shows how you can use the `st-login-form` component to create user-login forms for Streamlit apps."
)

st.write("1. Install")
st.code("pip install st-login-form", language="bash")
st.write("2. Import")
st.code("from st_login_form import login_form", language="python")
st.write("3. Use")
st.code("client = login_form()", language="python")
st.success("Explore the arguments you can pass to `login_form()`")
st.write(
    "`login_form()` creates the below form and returns the `Supabase.client` instance that can then be used to perform downstream supabase operations"
)

client = st_login_form.login_form(user_tablename="demo_users")

st.write(
    "On authentication, `login_form()` sets the `st.session_state['authenticated']` to `True`. This also collapses and disables the login form."
)
st.write(
    "`st.session_state['username']` is set to the provided username for a new or existing user, and to `None` for guest login."
)

if st.session_state["authenticated"]:
    if st.session_state["username"]:
        st.success(f"Welcome {st.session_state['username']}")
    else:
        st.success("Welcome guest")
else:
    st.error("Not authenticated")
