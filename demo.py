try:
    import inspect
    import traceback

    import streamlit as st
    from st_social_media_links import SocialMediaIcons
    from streamlit.components.v1 import html as st_html

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
        st_html(sidebar_html, height=290)

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
    st.title("🔐 `st-login-form` demo")

    st.write(
        "This app shows how you can use [`st-login-form`](https://github.com/SiddhantSadangi/st_login_form) to create Supabase connected user-login forms for Streamlit apps."
    )

    with st.expander("Installation", icon=":material/install_desktop:", expanded=False):
        st.write("1. Install")
        st.code("pip install st-login-form", language="bash")
        st.write("2. Import")
        st.code("from st_login_form import login_form", language="python")
        st.write("3. Use")
        st.code("supabase_connection = login_form()", language="python")
        st.info(
            "Detailed installation instructions [here](https://github.com/SiddhantSadangi/st_login_form?tab=readme-ov-file#building_construction-installation)."
        )
        st.write(
            "`login_form()` creates the below form and, after successful authentication, returns the [`SupabaseConnection`](https://github.com/SiddhantSadangi/st_supabase_connection) instance that can then be used to perform downstream supabase operations"
        )
    with st.expander(
        "`login_form()` API reference",
        icon=":material/lightbulb:",
        expanded=False,
    ):
        st.code(inspect.getdoc(st_login_form.login_form), language="docstring")

    supabase_connection = st_login_form.login_form(user_tablename="demo_users")

    st.write(
        "On authentication, `login_form()` sets `st.session_state['authenticated']` to `True`. This also collapses and disables the login form."
    )
    st.write(
        "`st.session_state['username']` is set to the provided username for a new or existing user, and to `None` for guest login."
    )

    if st.session_state["authenticated"]:
        if st.session_state["username"]:
            st.success(f"Welcome __{st.session_state['username']}__")
        else:
            st.success("Welcome guest")
    else:
        st.error("Not authenticated")
except Exception as e:
    st.error(
        f"""The app has encountered an error:\n
`{e}`\n
Please create an issue [here](https://github.com/SiddhantSadangi/st_login_form/issues/new)
with the below traceback""",
        icon="🥺",
    )
    st.code(traceback.format_exc())

st.success(
    "[Star the repo](https://github.com/SiddhantSadangi/st_login_form) to show your :heart:",
    icon="⭐",
)
