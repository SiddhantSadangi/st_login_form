# :lock: Streamlit Login Form
[![Downloads](https://static.pepy.tech/personalized-badge/st-login-form?period=total&units=international_system&left_color=black&right_color=brightgreen&left_text=Downloads)](https://pepy.tech/project/st-login-form)

A Streamlit authentication component that creates a user login form connected to a Supabase DB.

![Form screenshot](assets/screenshot.png)


## :balloon: Try the Demo App
<div align="center">
    <a href="https://st-lgn-form.streamlit.app/">
        <img src="https://static.streamlit.io/badges/streamlit_badge_black_white.svg" alt="Open in Streamlit" style="height: 60px !important;width: 217px !important;">
    </a>
</div>

## :rocket: Features
- One-line authentication frontend  
- Password hashing using the award-winning [Argon2](https://github.com/p-h-c/phc-winner-argon2) algorithm  
- Create new account, login to existing account, or login as guest
- Hash existing plaintext passwords in one-line of code
- Auto-collapses and disables the form on successful authentication

## :building_construction: Installation

1. Install `st-login-form`
```sh
pip install st-login-form
```
2. Create a Supabase project as mentioned [here](https://docs.streamlit.io/knowledge-base/tutorials/databases/supabase#sign-in-to-supabase-and-create-a-project)
3. Create a table to store the usernames and passwords. A sample DDL query is shown below:
  ```sql
  CREATE TABLE users (
      username text not null default ''::text,
      password text not null,
      constraint users_pkey primary key (username),
      constraint users_username_key unique (username),
      constraint users_password_check check (
        (
          length(
            trim(
              both
              from
                password
            )
          ) > 1
        )
      ),
      constraint users_username_check check (
        (
          length(
            trim(
              both
              from
                username
            )
          ) > 1
        )
      )
    ) tablespace pg_default;
  ```
4. Follow the rest of the steps from [here](https://docs.streamlit.io/knowledge-base/tutorials/databases/supabase#copy-your-app-secrets-to-the-cloud) to connect your Streamlit app to Supabase


## :pen: Usage

On authentication, `login_form()` sets the `st.session_state['authenticated']` to `True`. This also collapses and disables the login form.  
`st.session_state['username']` is set to the provided username for a new or existing user, and to `None` for guest login.

```python
import streamlit as st

from st_login_form import login_form

client = login_form()

if st.session_state["authenticated"]:
    if st.session_state["username"]:
        st.success(f"Welcome {st.session_state['username']}")
        ...

    else:
        st.success("Welcome guest")
        ...
else:
    st.error("Not authenticated")
```

### :key: Hashing existing plaintext passwords

Plaintext password for a user is automatically hashed during a login attempt.

To bulk-update all existing plaintext passwords in the table, use the `hash_current_passwords()` method.

### :bulb: API Reference

- `login_form()`

  ```python
  def login_form(
      *,
      title: str = "Authentication",
      user_tablename: str = "users",
      username_col: str = "username",
      password_col: str = "password",
      create_title: str = "Create new account :baby: ",
      login_title: str = "Login to existing account :prince: ",
      allow_guest: bool = True,
      allow_create: bool = True,
      guest_title: str = "Guest login :ninja: ",
      create_username_label: str = "Create a unique username",
      create_username_placeholder: str = None,
      create_username_help: str = None,
      create_password_label: str = "Create a password",
      create_password_placeholder: str = None,
      create_password_help: str = "Password cannot be recovered if lost",
      create_submit_label: str = "Create account",
      create_success_message: str = "Account created and logged-in :tada:",
      login_username_label: str = "Enter your unique username",
      login_username_placeholder: str = None,
      login_username_help: str = None,
      login_password_label: str = "Enter your password",
      login_password_placeholder: str = None,
      login_password_help: str = None,
      login_submit_label: str = "Login",
      login_success_message: str = "Login succeeded :tada:",
      login_error_message: str = "Wrong username/password :x: ",
      guest_submit_label: str = "Guest login",
  ) -> Client:
      """Creates a user login form in Streamlit apps.

      Connects to a Supabase DB using `SUPABASE_URL` and `SUPABASE_KEY` Streamlit secrets.
      Sets `session_state["authenticated"]` to True if the login is successful.
      Sets `session_state["username"]` to provided username or new or existing user, and to `None` for guest login.

      Returns:
      Supabase client instance
      """
  ```

- `hash_current_passwords()`

  ```python
  def hash_current_passwords(
      user_tablename: str = "users",
      username_col: str = "username",
      password_col: str = "password",
  ) -> None:
      """Hashes all current plaintext passwords stored in a database table (in-place)."""
  ```

## :handshake: Get Involved!
Your feedback and contributions can help shape the future of Streamlit Login Form. If you have ideas or features you'd like to see, let's collaborate!

- **Contribute**: Submit PRs or open issues on GitHub.
- **Connect**: Have questions or suggestions? Reach out to me on [LinkedIn](https://linkedin.com/in/siddhantsadangi) or [email](mailto:siddhant.sadangi@gmail.com).


## :sparkling_heart: Support Streamlit Login Form
Love Streamlit Login Form? Here's how you can show your support:

- **Star**: Give us a star on GitHub and help spread the word!
- **Share**: Tell your friends and colleagues about us on social media.
- **Donate**: Buy me a coffee and fuel further development!

<p align="center">
    <a href="https://www.buymeacoffee.com/siddhantsadangi" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;">
    </a>
</p>

Thank you for supporting Streamlit Login Form!
