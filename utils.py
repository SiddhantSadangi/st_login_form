def custom_exception_handler(exception: Exception) -> None:
    import smtplib
    import ssl
    import traceback
    from datetime import datetime
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    import streamlit as st
    from streamlit import secrets

    # Still show the exception to the user (default behavior)
    st.exception(exception)

    # Collect context about the exception
    exception_data = {
        "exception_name": str(exception),
        "traceback": str(traceback.format_exc()).strip(),
        "user_name": getattr(st.user, "user_name", "unknown") if hasattr(st, "user") else "unknown",
        "timestamp": datetime.now().isoformat(),
        "app_name": "Streamlit Login Form Demo",
    }

    try:
        # Create message
        message = MIMEMultipart()
        message["From"] = f"{secrets['email']['sender_name']} <{secrets['email']['sender_email']}>"
        message["To"] = secrets["email"]["recipient_email"]
        message["Subject"] = f"Exception Occurred in {exception_data['app_name']}"

        # Add body to email - convert dict to string
        body = f"""
        <h2>Exception Report</h2>
        <p><strong>Exception:</strong> {exception_data["exception_name"]}</p>
        <p><strong>Timestamp:</strong> {exception_data["timestamp"]}</p>
        <p><strong>User:</strong> {exception_data["user_name"]}</p>
        <h3>Traceback:</h3>
        <pre>{exception_data["traceback"]}</pre>
        """
        message.attach(MIMEText(body, "html"))

        # Create SMTP session
        context = ssl.create_default_context()

        with smtplib.SMTP(secrets["email"]["smtp_server"], secrets["email"]["smtp_port"]) as server:
            server.starttls(context=context)
            server.login(
                secrets["email"]["sender_email"],
                secrets["email"]["sender_password"],
            )

            # Send email
            text = message.as_string()
            server.sendmail(
                secrets["email"]["sender_email"],
                secrets["email"]["recipient_email"],
                text,
            )
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
    return True
