import streamlit as st
from st_social_media_links import SocialMediaIcons

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
    st.components.v1.html(sidebar_html, height=243)

    st.html(
        """
        <div style="text-align:center; font-size:14px; color:lightgrey">
            <hr style="margin-bottom: 6%; margin-top: 0%;">
            Share the ❤️ on social media
        </div>"""
    )

    social_media_links = [
        "https://www.facebook.com/sharer/sharer.php?kid_directed_site=0&sdk=joey&u=https%3A%2F%2Fst-lgn-form.streamlit.app%2F&display=popup&ref=plugin&src=share_button",
        "https://www.linkedin.com/sharing/share-offsite/?url=https%3A%2F%2Fst-lgn-form.streamlit.app%2F",
        "https://x.com/intent/tweet?original_referer=http%3A%2F%2Flocalhost%3A8501%2F&ref_src=twsrc%5Etfw%7Ctwcamp%5Ebuttonembed%7Ctwterm%5Eshare%7Ctwgr%5E&text=Check%20out%20this%20Streamlit%20login%20demo%20app%20%F0%9F%8E%88&url=https%3A%2F%2Fst-lgn-form.streamlit.app%2F",
    ]

    social_media_icons = SocialMediaIcons(
        social_media_links, colors=["lightgray"] * len(social_media_links)
    )

    social_media_icons.render(sidebar=True)

    st.html(
        """
        <div style="text-align:center; font-size:12px; color:lightgrey">
            <hr style="margin-bottom: 6%; margin-top: 6%;">
            <a rel="license" href="https://creativecommons.org/licenses/by-nc-sa/4.0/">
                <img alt="Creative Commons License" style="border-width:0"
                    src="https://i.creativecommons.org/l/by-nc-sa/4.0/88x31.png" />
            </a><br><br>
            This work is licensed under a <b>Creative Commons
                Attribution-NonCommercial-ShareAlike 4.0 International License</b>.<br>
            You can modify and build upon this work non-commercially. All derivatives should be
            credited to Siddhant Sadangi and
            be licenced under the same terms.
        </div>
    """
    )

# ---------- MAIN PAGE ----------
st.title("🔐 [`st-login-form`](https://github.com/SiddhantSadangi/st_login_form) demo app")

st.write(
    "This app shows how you can use the `st-login-form` component to create user-login forms for Streamlit apps."
)

st.write("1. Install")
st.code("pip install st-login-form", language="bash")
st.write("2. Import")
st.code("from st_login_form import login_form", language="python")
st.write("3. Use")
st.code("client = login_form()", language="python")
st.info(
    "💡 Explore the arguments you can pass to `login_form()` in the [source](https://github.com/SiddhantSadangi/st_login_form/blob/main/src/st_login_form/__init__.py)"
)
st.write(
    "`login_form()` creates the below form and returns the `Supabase.client` instance that can then be used to perform downstream supabase operations"
)
client = st_login_form.login_form(user_tablename="demo_users")

st.write(
    "On authentication, `login_form()` sets `st.session_state['authenticated']` to `True`. This also collapses and disables the login form."
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

st.success(
    "[Star the repo](https://github.com/SiddhantSadangi/st_login_form) to show your :heart:",
    icon="⭐",
)
