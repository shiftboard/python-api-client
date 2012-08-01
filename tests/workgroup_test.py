import shiftboard
import unittest
from mock import MagicMock

class TestWorkgroups(unittest.TestCase):

    def setUp(self):
        self.session = shiftboard.Session('mock_access_key', 'mock_signature_key', url='mock_url') 
        self.session.apicall = MagicMock(name='apicall')

        # setup the mock result
        self.session.apicall.return_value = {
            "seconds": "0.051276",
            "jsonrpc": "2.0",
            "id": "21",
            "result": {
                "count": "1",
                "workgroups": [
                    {
                        "code": "thecode",
                        "org_default": True,
                        "auto_add": True,
                        "timezone": "Greenwich Mean Time : Dublin, Lisbon, London (GMT)",
                        "self_remove": True,
                        "id": "226093",
                        "city": "Beverly Hills",
                        "public_phone": "5555551212",
                        "zip": "90210",
                        "office_phone": "5555551212",
                        "pager": "5555551212",
                        "cancel_period": "5",
                        "state": "California",
                        "location": "29120",
                        "show_confirmed": True,
                        "public_info": "some public info",
                        "member_add_shift": False,
                        "fax": "5555551212",
                        "mobile_phone": "5555551212",
                        "description": "some info",
                        "view_public": True,
                        "address": "1 Main St",
                        "other_phone": "5555551212",
                        "public_email": "test@servola.org",
                        "view_public_non_org": True,
                        "allowed_conflict_mins": "90",
                        "name": "Test Workgroup",
                        "public_code": "public code",
                        "contact_account": "948",
                        "url": "http://www.servola.org/",
                        "country": "USA",
                        "show_open": True,
                        "allow_shared": True
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

    def test_workgroup_list(self):
        workgroups = self.session.Workgroups()
        self.assertEqual(len(workgroups), 1)
        workgroup = workgroups[0]
        self.assertEqual(workgroup.get('name'), "Test Workgroup")
        self.assertEqual(workgroup.fullName(), "Test Workgroup")
        same_workgroup = workgroups[0]
        self.assertEqual(workgroup, same_workgroup)

    def test_workgroup_single(self):
        workgroup = self.session.Workgroup(id=226093)
        self.assertEqual(workgroup.get('name'), "Test Workgroup")
        self.assertEqual(workgroup.fullName(), "Test Workgroup")
        self.assertEqual(workgroup.get('address'), "1 Main St")
        self.assertEqual(workgroup.get('description'), "some info")
        self.assertTrue(workgroup.get('show_open'))
        self.assertFalse(workgroup.get('member_add_shift'))
        same_workgroup = self.session.Workgroup(id=226093)
        self.assertEqual(workgroup, same_workgroup)

if __name__ == '__main__':
    unittest.main()
