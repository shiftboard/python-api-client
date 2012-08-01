"""
Low-level interface for making API calls

Synopsis:

  session = Session(key_id, key)
  results = session.apicall('account.self')['result']
  print 'my first name is: %s' % (results['first_name'],)

  me = session.MyAccount()
  print 'my name is: %s' % (me.fullName(),)

"""
import shiftboard.session

from shiftboard.call import _ApiCall, _ApiCallJson, _ApiCallToken
from shiftboard.account import Account, MyAccount, Accounts
from shiftboard.workgroup import Workgroup, Workgroups
from shiftboard.location import Location, Locations
from shiftboard.shift import Shift, Shifts, ExtendedShifts, WhosOnShifts
from shiftboard.timeclock import Timeclock, WhosOnTimeclocks

URL = 'https://www.shiftboard.com/servola/api/api.cgi'

class Session(object):
    """Implement an API session, storing session data and transaction ID"""

    def __init__(self, access_key_id, signature_key, url=URL, id=1):
        self.access_key_id = access_key_id
        self.signature_key = signature_key
        self.url = url
        self.id = id - 1

    def apicall(self, method, **kwargs):
        """Make an API call"""
        self.id += 1
        api_handle = _ApiCall(self, method)
        return api_handle.get_result(kwargs)

    def __getattr__(self, name, *args, **kwargs):
        """Here we return any sort of API object-wrapper we may have included
        in this module, initialized with the arguments provided as well as a
        reference to this session."""

        cls = getattr(shiftboard.session, name)
        def callable(*args, **kwargs):
            return cls(self, *args, **kwargs)
        return callable

    def __str__(self):
        return """%s
    access_key_id: %s
    signature_key: %s
    url: %s""" % (self.__class__.__name__, self.access_key_id, self.signature_key, self.url)

class TokenSession(Session):
    """Session that authenticates using token (in addition to system API key)"""
    def __init__(self, token, *args, **kwargs):
        self.token = token
        super(TokenSession, self).__init__(*args, **kwargs)

    def call(self, name):
        self.id += 1
        return _ApiCallToken(self, name)

    def __str__(self):
        return """%s
    token: %s""" % (super(TokenSession, self).__str__(), self.token)
