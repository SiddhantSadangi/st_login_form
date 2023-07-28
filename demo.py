import streamlit as st

import st_login_form

VERSION = st_login_form.__version__

# ---------- SIDEBAR ----------
with open("assets/sidebar.html", "r", encoding="UTF-8") as sidebar_file:
    sidebar_html = sidebar_file.read().replace("{VERSION}", VERSION)

with st.sidebar:
    st.components.v1.html(sidebar_html, height=600)

# ---------- MAIN PAGE ----------
st.title("[`st-login-form`](https://github.com/SiddhantSadangi/st_login_form) demo app :star: ")

st.write(
    "This app shows how you can use the `st-login-form` component to create user-login forms for Streamlit apps."
)

client = st_login_form.login_form(user_tablename="demo_users")

if st.session_state["authenticated"]:
    if st.session_state["username"]:
        st.success(f"Welcome {st.session_state['username']}")
    else:
        st.success("Welcome guest")
else:
    st.error("Not authenticated")
