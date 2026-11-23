import unittest
from datetime import datetime, timezone, timedelta

from app import create_app, db
from app.models import User
from app.services.user_token_service import UserTokenService
from config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'


class TestUserTokenService(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.user = User(
            username='alice',
            email='alice@example.com'
        )
        db.session.add(self.user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_generate_token(self):
        token = UserTokenService.get_token(self.user, expires_in=3600)

        self.assertIsNotNone(token)
        self.assertIsInstance(token, str)
        self.assertEqual(len(token), 32)
        self.assertIsNotNone(self.user.token_expiration)

    def test_reuse_valid_token(self):
        first_token = UserTokenService.get_token(self.user)
        second_token = UserTokenService.get_token(self.user)

        self.assertEqual(first_token, second_token)

    def test_revoke_token(self):
        UserTokenService.get_token(self.user)

        UserTokenService.revoke_token(self.user)

        self.assertLess(
            self.user.token_expiration.replace(tzinfo=timezone.utc),
            datetime.now(timezone.utc)
        )

    def test_check_valid_token(self):
        token = UserTokenService.get_token(self.user)

        result = UserTokenService.check_token(token)

        self.assertEqual(result, self.user)

    def test_check_invalid_token(self):
        result = UserTokenService.check_token('token_inexistente')

        self.assertIsNone(result)

    def test_check_expired_token(self):
        self.user.token = 'token_expirado'
        self.user.token_expiration = (
            datetime.now(timezone.utc) - timedelta(seconds=10)
        )
        db.session.commit()

        result = UserTokenService.check_token(self.user.token)

        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()