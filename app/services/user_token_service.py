from datetime import datetime, timezone, timedelta
import secrets
import sqlalchemy as sa

from app import db
from app.models import User


class UserTokenService:

    @staticmethod
    def get_token(user, expires_in=3600):
        now = datetime.now(timezone.utc)

        if (user.token and user.token_expiration and
                user.token_expiration.replace(tzinfo=timezone.utc) >
                now + timedelta(seconds=60)):
            return user.token

        user.token = secrets.token_hex(16)
        user.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(user)

        return user.token

    @staticmethod
    def revoke_token(user):
        user.token_expiration = (
            datetime.now(timezone.utc) - timedelta(seconds=1)
        )

    @staticmethod
    def check_token(token):
        user = db.session.scalar(
            sa.select(User).where(User.token == token)
        )

        if (user is None or
                user.token_expiration is None or
                user.token_expiration.replace(tzinfo=timezone.utc) <
                datetime.now(timezone.utc)):
            return None

        return user