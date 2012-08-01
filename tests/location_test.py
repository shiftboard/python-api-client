import shiftboard
import unittest
from mock import MagicMock

class TestLocations(unittest.TestCase):

    def setUp(self):
        self.session = shiftboard.Session('mock_access_key', 'mock_signature_key', url='mock_url') 
        self.session.apicall = MagicMock(name='apicall')

        # setup the mock result
        self.session.apicall.return_value = {
            "seconds": "0.052861",
            "jsonrpc": "2.0",
            "id": "10",
            "result": {
                "count": "1",
                "locations": [
                    {
                        "latlon": "",
                        "city": "Beverly Hills",
                        "zip": "90210",
                        "name": "location 556",
                        "contact_last_name": "Perry",
                        "country": "USA",
                        "notes": "That's where we want to be",
                        "state": "California",
                        "special_instructions": "Livin' in Beverly Hills",
                        "contact_email": "test@example.com",
                        "contact_first_name": "Luke",
                        "address": "1 Main St",
                        "address_second": "Apt 1I",
                        "contact_phone": "555-555-1212",
                        "id": "29117"
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

    def test_location_list(self):
        locations = self.session.Locations( select = {"location": "29117"} )
        self.assertEqual(len(locations), 1)
        location = locations[0]
        self.assertEqual(location.get('address'), "1 Main St")
        self.assertEqual(location.get('city'), "Beverly Hills")
        self.assertEqual(location.get('state'), "California")
        self.assertEqual(location.get('zip'), "90210")
        self.assertEqual(location.get('notes'), "That's where we want to be")
        self.assertEqual(location.get('contact_first_name'), "Luke")
        self.assertEqual(location.get('contact_last_name'), "Perry")
        same_location = locations[0]
        self.assertEqual(location, same_location)

    def test_location_single(self):
        location = self.session.Location(id=29117)
        self.assertEqual(location.get('city'), "Beverly Hills")
        self.assertEqual(location.get('zip'), "90210")
        self.assertEqual(location.get('notes'), "That's where we want to be")
        same_location = self.session.Location(id=29117)
        self.assertEqual(location, same_location)


if __name__ == '__main__':
    unittest.main()
