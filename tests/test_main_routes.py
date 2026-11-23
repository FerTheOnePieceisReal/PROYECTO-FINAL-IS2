import unittest
from unittest.mock import patch

from app import create_app, db
from app.models import User, Post
from config import Config


class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    ELASTICSEARCH_URL = None


class TestMainRoutes(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        user = User(username='joaquin', email='joaquin@example.com')
        user.set_password('clave123')
        db.session.add(user)
        db.session.commit()
        self.user_id = user.id

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login(self):
        return self.client.post('/auth/login', data={
            'username': 'joaquin',
            'password': 'clave123'
        })

    @patch('app.main.routes.detect', return_value='en')
    def test_authenticated_user_can_publish_post(self, mock_detect):
        self.login()

        response = self.client.post('/index', data={
            'post': 'Hello world'
        })

        self.assertEqual(response.status_code, 302)

        post = db.session.scalar(db.select(Post))
        self.assertIsNotNone(post)
        self.assertEqual(post.body, 'Hello world')
        self.assertEqual(post.language, 'en')
        self.assertEqual(post.user_id, self.user_id)

    def test_empty_post_is_not_published(self):
        self.login()

        response = self.client.post('/index', data={'post': ''})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(db.session.scalar(db.select(db.func.count()).select_from(Post)), 0)

    def test_unauthenticated_user_is_redirected(self):
        response = self.client.get('/index')

        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/login', response.location)


if __name__ == '__main__':
    unittest.main()