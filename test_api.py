import unittest
import json
from app import create_app, db
from app.models import User, Task
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://' 

class APITestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def _get_auth_token(self):
        """Helper function to register a user and get a token."""
        self.client.post('/auth/register', data=json.dumps({
            'username': 'testuser',
            'password': 'password'
        }), content_type='application/json')

        res = self.client.post('/auth/login', data=json.dumps({
            'username': 'testuser',
            'password': 'password'
        }), content_type='application/json')
        return json.loads(res.data)['token']

    def test_registration(self):
        """Test user registration."""
        res = self.client.post('/auth/register', data=json.dumps({
            'username': 'newuser',
            'password': 'newpassword'
        }), content_type='application/json')
        self.assertEqual(res.status_code, 201)

    def test_login(self):
        """Test user login and token generation."""
        token = self._get_auth_token()
        self.assertIsNotNone(token)

    def test_create_task(self):
        """Test creating a new task."""
        token = self._get_auth_token()
        res = self.client.post('/tasks', headers={
            'Authorization': f'Bearer {token}'
        }, data=json.dumps({
            'title': 'My First Task'
        }), content_type='application/json')
        self.assertEqual(res.status_code, 201)
        self.assertIn('My First Task', str(res.data))

    def test_get_tasks(self):
        """Test retrieving tasks."""
        token = self._get_auth_token()
      
        self.client.post('/tasks', headers={'Authorization': f'Bearer {token}'},
                         data=json.dumps({'title': 'Task to retrieve'}),
                         content_type='application/json')

        res = self.client.get('/tasks', headers={'Authorization': f'Bearer {token}'})
        self.assertEqual(res.status_code, 200)
        self.assertIn('Task to retrieve', str(res.data))

if __name__ == '__main__':
    unittest.main()