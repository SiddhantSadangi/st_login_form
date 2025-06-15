from typing import Optional

import argon2
import streamlit as st
from supabase import Client


def _validate_password(
    password: str, min_length: int = 8, special_chars: str = "@$!%*?&_^#- "
) -> bool:
    """
    Validate a password against minimum length and character requirements.

    Args:
        password (str): The password to validate.
        min_length (int, optional): Minimum length required. Defaults to 8.
        special_chars (str, optional): String of allowed special characters. Defaults to '@$!%*?&_^#- '.

    Returns:
        bool: True if password meets all requirements, False otherwise.
    """
    required_chars = [
        lambda s: any(x.isupper() for x in s),
        lambda s: any(x.islower() for x in s),
        lambda s: any(x.isdigit() for x in s),
        lambda s: any(x in special_chars for x in s),
    ]
    return len(password) >= min_length and all(check(password) for check in required_chars)


def _set_authenticated(username: Optional[str] = None) -> None:
    """
    Set the session state to authenticated and store the username (or None for guest).

    Args:
        username (Optional[str]): The username to store, or None for guest.
    """
    st.session_state["authenticated"] = True
    st.session_state["username"] = username


def _reset_authentication() -> None:
    """
    Reset the session state to unauthenticated.
    """
    st.session_state["authenticated"] = False
    st.session_state["username"] = None


class _Authenticator(argon2.PasswordHasher):
    """
    A class derived from `argon2.PasswordHasher` to provide functionality for the authentication process.
    """

    def generate_pwd_hash(self, password: str) -> str:
        """
        Generates a hashed version of the provided password using `argon2`.

        Args:
            password (str): The plaintext password to hash.

        Returns:
            str: The hashed password, or the original if already hashed.
        """
        return password if password.startswith("$argon2id$") else self.hash(password)

    def verify_password(self, hashed_password: str, plain_password: str) -> Optional[bool]:
        """
        Verifies if a plaintext password matches a hashed one using `argon2`.

        Args:
            hashed_password (str): The hashed password from the database.
            plain_password (str): The plaintext password to verify.

        Returns:
            bool: True if the password matches, False otherwise.
        """
        try:
            if self.verify(hashed_password, plain_password):
                return True
        except argon2.exceptions.VerificationError:
            return False

    def rehash_pwd_in_db(
        self,
        password: str,
        username: str,
        client: Client,
        user_tablename: str,
        password_col: str,
        username_col: str,
    ) -> str:
        """A procedure to rehash given password in the db if necessary."""
        hashed_password = self.generate_pwd_hash(password)
        client.table(user_tablename).update({password_col: hashed_password}).match(
            {username_col: username}
        ).execute()

        return hashed_password
