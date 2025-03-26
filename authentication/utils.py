import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from django.conf import settings
import os
from dotenv import load_dotenv
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

load_dotenv()

BREVO_API_KEY = os.getenv("BREVO_API_KEY")
EMAIL_SENDER = "dev@una-oic.org"

def generate_reset_link(user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    reset_link = f"https://una-email-system-yvky.onrender.com/auth/password-reset-confirm/{uid}/{token}/"
    return reset_link

def send_reset_password_email(user):
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = BREVO_API_KEY
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

    reset_link = generate_reset_link(user)
    email_content = f"""
        <h3>Password Reset Requested</h3>
        <p>Hi {user.username},</p>
        <p>Please click the link below to reset your password:</p>
        <a href="{reset_link}">Reset Your Password</a>
        <p>If you didn't request this, please ignore this email.</p>
    """

    send_email = {
        "sender": {"email": EMAIL_SENDER, "name": "UNA Email System"},
        "to": [{"email": user.email, "name": user.username}],
        "subject": "Reset Your Password",
        "htmlContent": email_content
    }

    try:
        api_instance.send_transac_email(send_email)
        print(f"Password reset email sent to {user.email}")
        return True
    except ApiException as e:
        print(f"Error sending reset password email: {e}")
        return False
