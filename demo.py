import streamlit as st

from st_login_form import login_form

client = login_form(user_tablename="demo_users")

if st.session_state["authenticated"]:
    if st.session_state["username"]:
        st.success(f"Welcome {st.session_state['username']}")
    else:
        st.success("Welcome guest")
else:
    st.error("Not authenticated")
