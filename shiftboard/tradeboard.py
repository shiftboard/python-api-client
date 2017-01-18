"""
Classes to represent the tradeboard
"""

from result import *


class Trade(Result):
    """Represents a single trade"""
    name = 'trade'
    name_plural = 'tradeboard'

    def __init__(self, *initial_data, **kwargs):
        super(Trade, self).__init__(*initial_data, **kwargs)
        if len(initial_data) > 1:
            self.createRequest(initial_data[1], **kwargs)

    def getData(self):
        """Fetch one trade from the API"""
        result = self.session.apicall('tradeboard.get', id=self['id'])
        return result['result']['shift']

    def createRequest(self, *initial_data, **kwargs):
        """Create a trade request"""
        for dictionary in initial_data:
            for key in dictionary:
                self[key] = dictionary[key]
        for key in kwargs:
            self[key] = kwargs[key]
        trade_dict = self.copy()
        trade_dict.pop("session", None)

        result = self.session.apicall('tradeboard.create', **trade_dict)


class Trades(Results):
    """Represents a list of shifts on the Tradeboard"""

    child = Trade

    def storeBatch(self, obj):
        Results.storeBatch(self, obj)
        if 'referenced_objects' in obj and int(obj['count']) > 0:
            robjs = obj['referenced_objects']

            # index objects by most likely unique key
            objidx = dict()
            for objname, objarr in robjs.iteritems():
                for robj in objarr:
                    if 'id' in robj:
                        objidx.setdefault(objname, dict())[robj['id']] = robj
                    elif 'name' in robj:
                        objidx.setdefault(objname, dict())[robj['name']] = robj
            start = obj['page']['this']['start'] - 1
            for idx in range(start, start + len(obj[self.child.name_plural])):
                self.storage[idx].denormalizeReferenced(objidx)

    def getData(self, page={}):
        page['batch'] = self.batch
        return self.session.apicall('tradeboard.list', select=self.select, page=page)
