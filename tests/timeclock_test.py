import shiftboard
import unittest
from mock import MagicMock

class TestTimeclocks(unittest.TestCase):

    def setUp(self):
        self.session = shiftboard.Session('mock_access_key', 'mock_signature_key', url='mock_url') 
        self.session.apicall = MagicMock(name='apicall')

    def test_timeclock_list(self):
        # setup the mock result
        self.session.apicall.return_value = {
            "seconds": "0.081305",
            "jsonrpc": "2.0",
            "id": "1",
            "result": {
                "timeclocks": [
                    {
                        "account": "14",
                        "workgroup": "130815",
                        "clocked_in": "2012-07-24T22:40:16Z",
                        "shift": None,
                        "can_clockout": True,
                        "clocked_out": None
                    }
                ],
                "count": "1",
                "referenced_objects": {
                    "account": [
                        {
                            "first_name": "Joe",
                            "last_name": "Testing",
                            "id": "14",
                            "screen_name": "Joe Testing"
                        }
                    ],
                    "workgroup": [
                        {
                            "name": "Test Workgroup",
                            "id": "130815"
                        }
                    ]
                },
                "page": {
                    "this": {
                        "start": 1,
                        "batch": 10
                    }
                }
            }
        }

        timeclocks = self.session.WhosOnTimeclocks()
        self.assertEqual(len(timeclocks), 1)
        timeclock = timeclocks[0]
        self.assertEqual(timeclock['workgroup']['id'], "130815")
        self.assertEqual(timeclock['workgroup'].fullName(), "Test Workgroup")
        self.assertEqual(timeclock['account'].fullName(), "Joe Testing")
        self.assertTrue(timeclock.get('clocked_in'))
        self.assertTrue(timeclock.get('can_clockout'))
        self.assertFalse(timeclock.get('clocked_out'))
        self.assertTrue(timeclock.time())
        same_timeclock = timeclocks[0]
        #self.assertEqual(timeclock, same_timeclock)

    def test_timeclock_single(self):
        # setup the mock result
        self.session.apicall.return_value = {
            "seconds": "0.015229",
            "jsonrpc": "2.0",
            "id": "2",
            "result": {
                "account": "14",
                "clocked_out": None,
                "workgroup": "130815",
                "clocked_in": "2012-07-24T22:40:16Z"
            }
        }

        timeclock = self.session.Timeclock(id=14)
        self.assertEqual(timeclock.get('workgroup'), "130815")
        self.assertFalse(timeclock.get('clocked_out'))
        self.assertEqual(timeclock.get('account'), "14")
        same_timeclock = self.session.Timeclock(id=14)
        #self.assertEqual(timeclock, same_timeclock)


if __name__ == '__main__':
    unittest.main()
