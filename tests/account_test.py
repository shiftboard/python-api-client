import shiftboard
import unittest
from mock import MagicMock

class TestAccounts(unittest.TestCase):

    def setUp(self):
        self.session = shiftboard.Session('mock_access_key', 'mock_signature_key', url='mock_url') 
        self.session.apicall = MagicMock(name='apicall')

        # setup the mock result
        self.session.apicall.return_value = {
            "seconds": "0.015316",
            "jsonrpc": "2.0",
            "id": "3",
            "result": {
                "count": "1",
                "accounts": [
                    {
                        "last_name": "Testing",
                        "surname": "",
                        "timezone": "Pacific Time (US/Can) (GMT-08:00)",
                        "id": "2",
                        "city": "Seattle",
                        "first_name": "Joe",
                        "middle_name": "",
                        "zip": "98104",
                        "title": "",
                        "pager": "",
                        "state": "Washington",
                        "home_phone": "18007467531",
                        "email": "132997@servola.org",
                        "fax": "",
                        "mobile_phone": "",
                        "profile_type": "1",
                        "address": "123 Tiger Lane",
                        "other_phone": "",
                        "bad_email": False,
                        "url": "",
                        "country": "United States",
                        "region": "",
                        "org_hold": False,
                        "org_pending": "0"
                    }
                ],
                "page": {
                    "this": {
                        "start": 1,
                        "batch": 25
                    }
                }
            }
        }

    def test_account_list(self):
        accounts = self.session.Accounts()
        self.assertEqual(len(accounts), 1)
        account = accounts[0]
        self.assertTrue(account.fullName())
        same_account = accounts[0]
        self.assertEqual(account, same_account)

    def test_account_single(self):
        account = self.session.Account(id=2)
        self.assertEqual(account['first_name'], "Joe")
        self.assertEqual(account['last_name'], "Testing")
        self.assertEqual(account.fullName(), "Joe Testing")
        same_account = self.session.Account(id=2)
        self.assertEqual(account, same_account)


if __name__ == '__main__':
    unittest.main()
