RPCVER = '2.0'

import hmac
import hashlib
import httplib
import urllib
import urllib2
import datetime

# Different versions of Python have a different name for the JSON library.
try:
    import simplejson as json
except ImportError:
    import json


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, datetime.datetime):
        serial = obj.isoformat()
        return serial
    if isinstance(obj, datetime.date):
        serial = obj.isoformat()
        return serial
    raise TypeError("Type not serializable")


# track most recent url for debugging
lasturl = None

LOGREQUEST = False;
LOGRESPONSE = False;
# LOGREQUEST=True; LOGRESPONSE=False;
# LOGREQUEST=True; LOGRESPONSE=True;

if LOGREQUEST or LOGRESPONSE:
    try:
        import log
    except ImportError:
        pass


class RPCError(Exception):
    def __init__(self, code, message, method, params):
        self.code = code
        self.message = message
        self.method = method
        self.params = params

    def __repr__(self):
        return str(self)

    def __str__(self):
        return '<%s %s: %s method:%s params:%r>' % (
            self.__class__.__name__, self.code, self.message, self.method, self.params)


class RPCServerError(RPCError):
    """Exception representing an rpc error response"""

    def __init__(self, json_error_struct, method, params):
        RPCError.__init__(
            self,
            json_error_struct['data']['code'],
            json_error_struct['data'].get('message', ''),
            method,
            params
        )


class RPCClientError(RPCError):
    pass


class _ApiCallJson(object):
    """Callable class to return from session.__attr__ implementing arbitrary
    API call.  Accepts and returns json strings."""

    def __init__(self, session, method):
        """Save session attributes & method name during construction"""
        self.session = session
        self.method = method

    def __call__(self, json_params):
        """Take params when called"""
        result = self.get_result_json(json_params)
        return result

    @staticmethod
    def _b64(s):
        """Encode a string with base64"""
        return s.encode('base64').strip()

    @property
    def command(self):
        return 'method' + self.method + 'params' + self.json_params

    @property
    def digest(self):
        return hmac.HMAC(
            str(self.session.signature_key),
            self.command,
            hashlib.sha1
        )

    @property
    def urlparts(self):
        return {
            'id': self.session.id,
            'jsonrpc': RPCVER,
            'method': self.method,
            'access_key_id': self.session.access_key_id,
            'signature': self._b64(self.digest.digest()),
            'params': self._b64(self.json_params),
        }

    @property
    def url(self):
        global lasturl
        url = self.session.url + '?' + urllib.urlencode(self.urlparts)
        lasturl = url
        return url

    def get_result_json(self, json_params):
        """Override from base class, using token in request"""
        self.json_params = json_params
        self.logRequest(json_params)
        try:
            conn = urllib2.urlopen(self.url)
        except urllib2.HTTPError, e:
            raise RPCClientError(1, 'Error opening %s' % self.session.url,
                                 self.method, json_params)
        result = conn.read()
        self.logResponse(result)
        return result

    def logRequest(self, request):
        """Pretty-print the request if request logging enabled"""
        if LOGREQUEST:
            log.warn('REQUEST (%s): %s\n  %s\n%s' %
                     (self.__class__.__name__,
                      self.method, self.command, self._prettify(request),))

    def logResponse(self, result):
        """Pretty-print the response if response logging enabled"""
        if LOGRESPONSE:
            log.warn('RESPONSE to %s: %s' %
                     (self.method, self._prettify(result),))

    def _prettify(self, json_obj):
        """De+encode json with pretty-printing"""
        return json.dumps(json.loads(json_obj),
                          sort_keys=True, indent='    ',
                          )


class _ApiCall(_ApiCallJson):
    """Extend API callable class to accept & return python structures."""

    def get_result(self, params):
        # Convert date and datetime objects to serializable forms
        json_params = json.dumps(params, default=json_serial)
        result = self.get_result_json(json_params)
        result = json.loads(result)
        if 'error' in result:
            raise RPCServerError(result['error'], self.method, params)
        return result

    def __call__(self, *args, **kw):
        """Wrap parent class, creating and deconstructing JSON"""
        if args:
            if kw:
                raise ValueError('cant use args + kw')
            params = args
        else:
            params = kw
        self.get_result(params)


class _ApiCallToken(_ApiCall):
    """Extends for use with a token."""

    @property
    def command(self):
        command = super(_ApiCallToken, self).command
        command += 'token' + self.session.token
        return command

    @property
    def urlparts(self):
        parts = super(_ApiCallToken, self).urlparts
        parts['token'] = self.session.token
        return parts
