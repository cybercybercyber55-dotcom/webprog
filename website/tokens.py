# website/tokens.py

from itsdangerous import URLSafeTimedSerializer
from flask import current_app


def generate_reset_token(email):
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return s.dumps(email, salt=current_app.config['SECURITY_PASSWORD_SALT'])


def verify_reset_token(token, expiration=3600):
    """
    expiration: seconds (3600 = 1 hour)
    Returns email if valid, otherwise None.
    """
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = s.loads(
            token,
            salt=current_app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
    except Exception:
        return None
    return email
