import streamlit as st
from st_supabase_connection import SupabaseConnection

from st_login_form import login_form

connection = st.connection(name="supabase", type=SupabaseConnection)


class DummyClient:
    pass


st.write(connection)
if connection := login_form(user_tablename="demo_users"):
    st.write(connection)
    st.write(connection.table("cities").select("*").execute())
