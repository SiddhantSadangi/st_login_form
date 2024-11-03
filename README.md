<h1 align="center"> 🔐 Streamlit Login Form </h1>

<div align="center">
    <img src="https://img.shields.io/pypi/v/st-login-form.svg" alt="PyPI downloads">
    <a href="https://pepy.tech/project/st-login-form"> <img src="https://static.pepy.tech/personalized-badge/st-login-form?period=total&left_text=Downloads"> </a>
    <img src="https://img.shields.io/github/license/SiddhantSadangi/st_login_form.svg" alt="License">
    <img src="https://img.shields.io/badge/PRs-Welcome-brightgreen.svg" alt="PRs Welcome">
    <br><br>
    A Streamlit authentication component that creates a user login form connected to a Supabase DB.
    <br><br>
    <img src="assets/screenshot.png" alt="App screenshot">
</div>

## :balloon: Try the Demo App
<div align="center">
    <a href="https://st-lgn-form.streamlit.app/">
        <img src="https://static.streamlit.io/badges/streamlit_badge_black_white.svg" alt="Open in Streamlit" style="height: 60px !important;width: 217px !important;">
    </a>
</div>

## :rocket: Features
- One-line authentication frontend  
- Password hashing using the award-winning [Argon2](https://github.com/p-h-c/phc-winner-argon2) algorithm  
- Inbuilt password constraint checks
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
      icon: str = ":material/lock:",
      user_tablename: str = "users",
      username_col: str = "username",
      password_col: str = "password",
      constrain_password: bool = True,
      create_title: str = ":material/add_circle: Create new account",
      login_title: str = ":material/login: Login to existing account",
      allow_guest: bool = True,
      allow_create: bool = True,
      guest_title: str = ":material/visibility_off: Guest login",
      create_username_label: str = "Create a unique username",
      create_username_placeholder: str = None,
      create_username_help: str = None,
      create_password_label: str = "Create a password",
      create_password_placeholder: str = None,
      create_password_help: str = ":material/warning: Password cannot be recovered if lost",
      create_submit_label: str = ":material/add_circle: Create account",
      login_username_label: str = "Enter your unique username",
      login_username_placeholder: str = None,
      login_username_help: str = None,
      login_password_label: str = "Enter your password",
      login_password_placeholder: str = None,
      login_password_help: str = None,
      login_submit_label: str = ":material/login: Login",
      login_error_message: str = ":material/lock: Wrong username/password",
      password_constraint_check_fail_message: str = ":material/warning: Password must contain at least 8 characters, including one uppercase letter, one lowercase letter, one number, and one special character (`@$!%*?&_^#- `).",
      guest_submit_label: str = ":material/visibility_off: Guest login",
  ) -> Client:
      """Creates a user login form in Streamlit apps.

      Connects to a Supabase DB using `SUPABASE_URL` and `SUPABASE_KEY` Streamlit secrets.
      Sets `session_state["authenticated"]` to True if the login is successful.
      Sets `session_state["username"]` to provided username or new or existing user, and to `None` for guest login.

      Arguments:
          title (str): The title of the login form. Default is "Authentication".
          icon (str): The icon to display next to the title. Default is ":material/lock:".
          user_tablename (str): The name of the table in the database that stores user information. Default is "users".
          username_col (str): The name of the column in the user table that stores usernames. Default is "username".
          password_col (str): The name of the column in the user table that stores passwords. Default is "password".
          constrain_password (bool): Whether to enforce password constraints (at least 8 characters, including one uppercase letter, one lowercase letter, one number, and one special character (`@$!%*?&_^#- `)). Default is True.
          create_title (str): The title of the create new account tab. Default is ":material/add_circle: Create new account".
          login_title (str): The title of the login to existing account tab. Default is ":material/login: Login to existing account".
          allow_guest (bool): Whether to allow guest login. Default is True.
          allow_create (bool): Whether to allow creating new accounts. Default is True.
          guest_title (str): The title of the guest login tab. Default is ":material/visibility_off: Guest login".
          create_username_label (str): The label for the create username input field. Default is "Create a unique username".
          create_username_placeholder (str): The placeholder text for the create username input field. Default is None.
          create_username_help (str): The help text for the create username input field. Default is None.
          create_password_label (str): The label for the create password input field. Default is "Create a password".
          create_password_placeholder (str): The placeholder text for the create password input field. Default is None.
          create_password_help (str): The help text for the create password input field. Default is ":material/warning: Password cannot be recovered if lost".
          create_submit_label (str): The label for the create account submit button. Default is ":material/add_circle: Create account".
          login_username_label (str): The label for the login username input field. Default is "Enter your unique username".
          login_username_placeholder (str): The placeholder text for the login username input field. Default is None.
          login_username_help (str): The help text for the login username input field. Default is None.
          login_password_label (str): The label for the login password input field. Default is "Enter your password".
          login_password_placeholder (str): The placeholder text for the login password input field. Default is None.
          login_password_help (str): The help text for the login password input field. Default is None.
          login_submit_label (str): The label for the login submit button. Default is ":material/login: Login".
          login_error_message (str): The error message displayed when the username or password is incorrect. Default is ":material/lock: Wrong username/password".
          password_constraint_check_fail_message (str): The error message displayed when the password does not meet the constraints. Default is ":material/warning: Password must contain at least 8 characters, including one uppercase letter, one lowercase letter, one number, and one special character (`@$!%*?&_^#- `).".
          guest_submit_label (str): The label for the guest login button. Default is ":material/visibility_off: Guest login".

      Returns:
          Supabase.client: The client instance for performing downstream supabase operations.
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

## :framed_picture: Gallery
Some notable Streamlit apps using `st-login-form`

- [SmartExam.io](https://smartexam.io/): SmartExam is an AI app that leverages University lectures to create interactive test exams.

_Want to feature your app? Create a PR!_

## :motorway:  Project Roadmap
Here are some features that are planned for future releases across the library and demo app. If you want to contribute to any of these features, feel free to open a PR!

### Library Features
- [ ] Add retype password for confirmation while signing up
- [ ] Customize password constraints (minimum length, allowed characters, etc.)
- [ ] Add logout option
- [ ] Capture additional login metadata - created_at, last_login_at, num_logins, etc.
- [ ] Add admin panel to set user roles and permissions
- [ ] Add password recovery option
- [ ] Support additional databases:
  - [ ] MySQL

### Demo App Features
- [ ] Allow users to customise demo login form  
- [ ] Add code preview for the rendered login form  

## :bow: Acknowledgements
- [Streamlit](https://streamlit.io) for the amazing Streamlit framework and promoting this library
- [Ahmed Ramadan](https://www.linkedin.com/in/theahmedrmdan/) for implementing password hashing
- Everyone who has shared feedback to improve this library!

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
