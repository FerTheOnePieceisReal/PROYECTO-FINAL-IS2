
import unittest
from app import create_app, db
from unittest.mock import patch
from app.models import User
from config import Config


class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    ELASTICSEARCH_URL = None


class TestAuthRoutes(unittest.TestCase):

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

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_login_success(self):
        response = self.client.post('/auth/login', data={
            'username': 'joaquin',
            'password': 'clave123'
        }, follow_redirects=False)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/index', response.location)

    def test_login_nonexistent_user(self):
        response = self.client.post('/auth/login', data={
            'username': 'inexistente',
            'password': 'clave123'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid username or password', response.data)

    def test_login_incorrect_password(self):
        response = self.client.post('/auth/login', data={
            'username': 'joaquin',
            'password': 'incorrecta'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid username or password', response.data)

    def test_login_external_redirect_is_rejected(self):
        response = self.client.post(
            '/auth/login?next=https://sitio-malicioso.com',
            data={
                'username': 'joaquin',
                'password': 'clave123'
            },
            follow_redirects=False
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn('/index', response.location)

    def test_authenticated_user_cannot_access_login(self):
        self.client.post('/auth/login', data={
            'username': 'joaquin',
            'password': 'clave123'
        })

        response = self.client.get('/auth/login')

        self.assertEqual(response.status_code, 302)
        self.assertIn('/index', response.location)


    def test_register_success(self):
        response = self.client.post('/auth/register', data={
            'username': 'nuevo_usuario',
            'email': 'nuevo@example.com',
            'password': 'clave123',
            'password2': 'clave123'
        }, follow_redirects=False)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/login', response.location)

        user = db.session.scalar(
            db.select(User).where(User.username == 'nuevo_usuario')
        )
        self.assertIsNotNone(user)
        self.assertTrue(user.check_password('clave123'))

    def test_register_duplicate_username(self):
        response = self.client.post('/auth/register', data={
            'username': 'joaquin',
            'email': 'otro@example.com',
            'password': 'clave123',
            'password2': 'clave123'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please use a different username.', response.data)

    def test_register_duplicate_email(self):
        response = self.client.post('/auth/register', data={
            'username': 'otro_usuario',
            'email': 'joaquin@example.com',
            'password': 'clave123',
            'password2': 'clave123'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please use a different email address.', response.data)


    @patch('app.auth.routes.send_password_reset_email')
    def test_reset_password_request_existing_email(self, mock_send_email):
        response = self.client.post('/auth/reset_password_request', data={
            'email': 'joaquin@example.com'
        }, follow_redirects=False)

        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/login', response.location)
        mock_send_email.assert_called_once()

    @patch('app.auth.routes.send_password_reset_email')
    def test_reset_password_request_nonexistent_email(self, mock_send_email):
        response = self.client.post('/auth/reset_password_request', data={
            'email': 'inexistente@example.com'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b'Check your email for the instructions to reset your password',
            response.data
        )
        mock_send_email.assert_not_called()

    def test_reset_password_invalid_token(self):
        response = self.client.get(
            '/auth/reset_password/token_invalido'
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn('/index', response.location)

    def test_reset_password_success(self):
        user = db.session.scalar(
            db.select(User).where(User.username == 'joaquin')
        )
        token = user.get_reset_password_token()

        response = self.client.post(
            f'/auth/reset_password/{token}',
            data={
                'password': 'nueva_clave123',
                'password2': 'nueva_clave123'
            },
            follow_redirects=False
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/login', response.location)

        self.assertTrue(user.check_password('nueva_clave123'))




if __name__ == '__main__':
    unittest.main(verbosity=2)
