import unittest
from datetime import datetime, timezone, timedelta
from app import create_app, db
from app.models import User
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'

class TestUserModel(unittest.TestCase):
    def setUp(self):
        # Inicializar (Arrange) el entorno de prueba
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        # Limpiar el entorno
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        # Arrange
        u = User(username='susan')
        # Act
        u.set_password('clave123')
        # Assert
        self.assertFalse(u.check_password('falsa456'))
        self.assertTrue(u.check_password('clave123'))

    def test_avatar(self):
        # Arrange
        u = User(username='john', email='test@example.com')
        # Act
        avatar_url = u.avatar(128)
        # Assert
        expected_url = 'https://www.gravatar.com/avatar/55502f40dc8b7c769880b10874abc9d0?d=identicon&s=128'
        self.assertEqual(avatar_url, expected_url)

    def test_follow_unfollow(self):
        # Arrange
        u1 = User(username='alice, email='alice@example.com'')
        u2 = User(username='bob', email='bob@example.com')
        db.session.add_all([u1, u2])
        db.session.commit()

        # Act & Assert - Estado inicial
        self.assertFalse(u1.is_following(u2))
        self.assertEqual(u1.following_count(), 0)
        
        # Act - Seguir
        u1.follow(u2)
        db.session.commit()
        # Assert - Seguir
        self.assertTrue(u1.is_following(u2))
        self.assertEqual(u1.following_count(), 1)
        self.assertEqual(u2.followers_count(), 1)

        # Act - Dejar de seguir
        u1.unfollow(u2)
        db.session.commit()
        # Assert - Dejar de seguir
        self.assertFalse(u1.is_following(u2))
        self.assertEqual(u1.following_count(), 0)

    def test_get_token(self):
        # Arrange
        u = User(username='charlie', email='charlie@example.com')
        db.session.add(u)
        db.session.commit()
        
        # Act
        token = u.get_token(expires_in=3600)
        db.session.commit()
        
        # Assert
        self.assertIsNotNone(token)
        self.assertIsInstance(token, str)
        self.assertGreater(u.token_expiration.replace(tzinfo=timezone.utc), datetime.now(timezone.utc))
