import unittest
from app import app

class FlaskAPITestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_api_endpoint(self):
        response = self.app.get('/api')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome to the Metal As Hell API!', response.data)

if __name__ == '__main__':
    unittest.main()