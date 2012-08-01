import shiftboard
import unittest
from mock import MagicMock

class TestSessionObject(unittest.TestCase):

    def setUp(self):
        self.session = shiftboard.Session('mock_access_key', 'mock_signature_key', url='mock_url') 
        #mock = MagicMock(spec=shiftboard._ApiCall)
        self.session.call = MagicMock(name='call')

    def test_instance(self):
        self.assertEqual(self.session.access_key_id, 'mock_access_key')
        self.assertEqual(self.session.signature_key, 'mock_signature_key')
        self.assertEqual(self.session.url, 'mock_url')

    def test_mock(self):
        result = self.session.call('account.list')( select = { id: 1 })
        self.session.call.assert_called_with('account.list')

if __name__ == '__main__':
    unittest.main()
