import shiftboard
import unittest
from mock import MagicMock

class TestShifts(unittest.TestCase):

    def setUp(self):
        self.session = shiftboard.Session('mock_access_key', 'mock_signature_key', url='mock_url') 
        self.session.apicall = MagicMock(name='apicall')

    def test_shift_list(self):
        # setup the mock result
        self.session.apicall.return_value = {
            "seconds": "0.081433",
            "jsonrpc": "2.0",
            "id": "44",
            "result": {
                "count": "1",
                "shifts": [
                    {
                        "count": "1",
                        "covering_workgroup": "226084",
                        "workgroup": "226084",
                        "end_date": "2010-09-17T14:30:00",
                        "id": "2753501",
                        "qty": "1",
                        "published": True,
                        "covered": True,
                        "timezone": "Greenwich Mean Time : Dublin, Lisbon, London (GMT)",
                        "start_date": "2010-09-17T14:00:00",
                        "subject": "Time to do something"
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

        shifts = self.session.Shifts( select = {"workgroup": "226084"} )
        self.assertEqual(len(shifts), 1)
        shift = shifts[0]
        self.assertEqual(shift.get('workgroup'), "226084")
        self.assertEqual(shift.get('covering_workgroup'), "226084")
        self.assertTrue(shift.get('published'))
        self.assertTrue(shift.get('covered'))
        self.assertEqual(shift.get('subject'), "Time to do something")
        self.assertTrue(shift.time())
        same_shift = shifts[0]
        #self.assertEqual(shift, same_shift)

    def test_shift_single(self):
        # setup the mock result
        self.session.apicall.return_value = {
            "seconds": "0.062897",
            "jsonrpc": "2.0",
            "id": "25",
            "result": {
                "shift": {
                    "count": "1",
                    "linktitle": "",
                    "details": "",
                    "room_floor": "",
                    "qty": "1",
                    "zipcode": "60616",
                    "start_date": "2010-09-17T12:00:00",
                    "urgent": False,
                    "workgroup": "226081",
                    "reference_id": "",
                    "published": False,
                    "covered": False,
                    "timezone": "Pacific Time (US/Can) (GMT-08:00)",
                    "subject": "Doing something else",
                    "linkurl": "",
                    "id": "2753499",
                    "no_pick_up": False,
                    "work_status_type": "0"
                }
            }
        }

        shift = self.session.Shift(id=2)
        self.assertEqual(shift.get('workgroup'), "226081")
        self.assertEqual(shift.get('covering_workgroup'), None)
        self.assertFalse(shift.get('published'))
        self.assertFalse(shift.get('covered'))
        self.assertEqual(shift.get('subject'), "Doing something else")
        same_shift = self.session.Shift(id=2)
        #self.assertEqual(shift, same_shift)

    def test_shift_page(self):
        # setup the mock result
        self.session.apicall.return_value = {
            "seconds": "0.081433",
            "jsonrpc": "2.0",
            "id": "44",
            "result": {
                "count": "5",
                "shifts": [
                    {
                        "count": "1",
                        "covering_workgroup": "226084",
                        "workgroup": "226084",
                        "end_date": "2010-09-17T14:30:00",
                        "id": "2753501",
                        "qty": "1",
                        "published": True,
                        "covered": True,
                        "timezone": "Greenwich Mean Time : Dublin, Lisbon, London (GMT)",
                        "start_date": "2010-09-17T14:00:00",
                        "subject": "Time to do something"
                    },
                    {
                        "count": "1",
                        "covering_workgroup": "226084",
                        "workgroup": "226084",
                        "end_date": "2010-09-17T15:30:00",
                        "id": "2753502",
                        "qty": "1",
                        "published": True,
                        "covered": True,
                        "timezone": "Greenwich Mean Time : Dublin, Lisbon, London (GMT)",
                        "start_date": "2010-09-17T15:00:00",
                        "subject": "Time to do something"
                    },
                    {
                        "count": "1",
                        "covering_workgroup": "226084",
                        "workgroup": "226084",
                        "end_date": "2010-09-17T16:30:00",
                        "id": "2753503",
                        "qty": "1",
                        "published": True,
                        "covered": True,
                        "timezone": "Greenwich Mean Time : Dublin, Lisbon, London (GMT)",
                        "start_date": "2010-09-17T16:00:00",
                        "subject": "Time to do something"
                    },
                    {
                        "count": "1",
                        "covering_workgroup": "226084",
                        "workgroup": "226084",
                        "end_date": "2010-09-17T17:30:00",
                        "id": "2753504",
                        "qty": "1",
                        "published": True,
                        "covered": True,
                        "timezone": "Greenwich Mean Time : Dublin, Lisbon, London (GMT)",
                        "start_date": "2010-09-17T17:00:00",
                        "subject": "Time to do something"
                    },
                    {
                        "count": "1",
                        "covering_workgroup": "226084",
                        "workgroup": "226084",
                        "end_date": "2010-09-17T18:30:00",
                        "id": "2753505",
                        "qty": "1",
                        "published": True,
                        "covered": True,
                        "timezone": "Greenwich Mean Time : Dublin, Lisbon, London (GMT)",
                        "start_date": "2010-09-17T18:00:00",
                        "subject": "Time to do something"
                    }
                ],
                "page": {
                    "this": {
                        "start": 1,
                        "batch": 5
                    },
                    "next": {
                        "start": 6,
                        "batch": 5
                    }
                }
            }
        }

        shifts = self.session.Shifts( select = {"workgroup": "226084"} )
        self.assertEqual(len(shifts), 5)
        self.assertEqual(shifts.page['next']['start'], 6)
        shift = shifts[4]
        self.assertEqual(shift.get('workgroup'), "226084")
        self.assertEqual(shift.get('covering_workgroup'), "226084")
        self.assertTrue(shift.get('published'))
        self.assertTrue(shift.get('covered'))
        self.assertEqual(shift.get('subject'), "Time to do something")
        self.assertTrue(shift.time())
        same_shift = shifts[4]
        #self.assertEqual(shift, same_shift)


if __name__ == '__main__':
    unittest.main()
