import unittest
from app import create_app, db
from app.models import User
from config import Config
from sqlalchemy.exc import IntegrityError


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'


class TestUserRepository(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_insert_user(self):
        # Arrange
        user = User(username='joaquin', email='joaquin@example.com')

        # Act
        db.session.add(user)
        db.session.commit()

        # Assert
        self.assertIsNotNone(user.id)
        saved_user = db.session.get(User, user.id)
        self.assertIsNotNone(saved_user)
        self.assertEqual(saved_user.username, 'joaquin')
        self.assertEqual(saved_user.email, 'joaquin@example.com')

    def test_find_user_by_id(self):
        # Arrange
        user = User(username='alice', email='alice@example.com')
        db.session.add(user)
        db.session.commit()
        user_id = user.id

        # Act
        found_user = db.session.get(User, user_id)

        # Assert
        self.assertIsNotNone(found_user)
        self.assertEqual(found_user.id, user_id)
        self.assertEqual(found_user.username, 'alice')

    def test_find_nonexistent_user(self):
        # Act
        found_user = db.session.get(User, 9999)

        # Assert
        self.assertIsNone(found_user)

    def test_update_user(self):
        # Arrange
        user = User(username='carlos', email='carlos@example.com')
        db.session.add(user)
        db.session.commit()
        user_id = user.id

        # Act
        user.username = 'carlos_actualizado'
        db.session.commit()

        # Limpiar la sesión para consultar nuevamente la BD
        db.session.expire_all()
        updated_user = db.session.get(User, user_id)

        # Assert
        self.assertIsNotNone(updated_user)
        self.assertEqual(updated_user.username, 'carlos_actualizado')

    
    def test_delete_user(self):
        # Arrange
        user = User(username='maria', email='maria@example.com')
        db.session.add(user)
        db.session.commit()
        user_id = user.id

        # Act
        db.session.execute(
            db.delete(User).where(User.id == user_id)
        )
        db.session.commit()

        # Assert
        deleted_user = db.session.get(User, user_id)
        self.assertIsNone(deleted_user)
    
    def test_duplicate_email(self):
        # Arrange
        user1 = User(
            username='usuario1',
            email='duplicado@example.com'
        )
        user2 = User(
            username='usuario2',
            email='duplicado@example.com'
        )

        db.session.add(user1)
        db.session.commit()

        # Act & Assert
        db.session.add(user2)

        with self.assertRaises(IntegrityError):
            db.session.commit()

        db.session.rollback()

