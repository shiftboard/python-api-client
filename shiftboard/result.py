
import shiftboard

class Result(dict):
    """Base class for single-record api responses"""

    def __init__(self, session, seed=None, id=None, **reqargs):
        super(Result, self).__init__()
        self.session = session
        self.loaded = False
        self.reqargs = reqargs

        if seed:
            self.update(seed)

        if id:
            self['id'] = id
            self.load()

    def load(self):
        """Merge loaded data into our (sparse) set"""
        if (self.loaded):
            return

        for key, val in self.getData().iteritems():
            if not key in self:
                self.setdefault(key, val)
        self.loaded = True

    def getData(self):
        """Often-overriden method for loading data from API"""
        return self.session.apicall('%s.list' % self.name,
            select = { self.name: self['id'] },
            extended = True,
            **self.reqargs
            )['result'][self.name_plural][0]

    def __hash__(self):
        return int(self['id'])

    def __eq__(self, other):
        return self.__class__ == other.__class__ and hash(self) == hash(other)


class Results(object):
    """Base class for multi-record api responses"""

    def __init__(self, session, select={}, batch=25, **reqargs):
        self.storage = dict()
        self.session = session
        self.select = select
        self.batch = batch
        self.reqargs = reqargs

    def loadBatch(self, idx):
        """Fetch some data and store it"""
        obj = self.getData({'start': idx})['result']
        self.storeBatch(obj)

    def storeBatch(self, obj):
        """Given the result of a fetch, store the data"""
        self.count = int(obj['count'])
        if self.count == 0:
            return

        self.page = obj['page']

        # convert to 0-index here:
        start = obj['page']['this']['start'] - 1
        for obj in obj[self.child.name_plural]:
            self.storage[start] = self.element(obj)
            start += 1

    def getData(self, page={}):
        """Make the API call to get some data"""
        page['batch'] = self.batch
        return self.session.apicall('%s.list' % self.child.name,
            select=self.select,
            page=page,
            **self.reqargs
            )

    def element(self, d):
        """Converts a dict of data to an element object"""
        return self.child(self.session, seed=d)

    def __repr__(self):
        return '%s list of %d virtual (%d stored)' % (
            self.__class__.__name__, len(self), len(self.storage))

    def __len__(self):
        try:
            return self.count
        except AttributeError:
            self.loadBatch(0)
            return self.count

    def __getitem__(self, idx):
        try:
            if idx > self.count:
                raise IndexError
            return self.storage[idx]
        except (KeyError, AttributeError):
            self.loadBatch(idx)
            return self.storage[idx]

    def __iter__(self):
        for idx in range(0, len(self)):
            yield self[idx]

    def __getslice__(self, start, end):
        d = []
        for idx in range(start, end):
            d.append(self[idx])
        return d

    def getAllValues(self, key):
        """get all the values from all the records for a given key"""
        vals = set()
        for rec in self:
            if key in rec and rec[key]:
                if isinstance(rec[key], dict) and 'id' in rec[key]:
                    vals.add(rec[key]['id'])
                else:
                    vals.add(rec[key])
        return vals

    def denormalize(self, cls, key=None, selectkey=None):
        """Replace id numbers in values with detail records

        { name: 'some object',
          location: 5
        }

        .. denormalize(Location) ..

        { name: 'some object',
          location:
            {
                id: 5,
                name: 'some location',
                etc..
            }
        }

        """

        key = key or cls.child.name
        selectkey = selectkey or cls.child.name
        ids = self.getAllValues(key)

        if not ids:
            return

        objects = dict(
            (o['id'], o) for o in cls(
                self.session,
                select = {selectkey: list(ids)},
                batch = shiftboard.MAX_BATCH_SIZE)
            )

        for rec in self:
            if key in rec and rec[key]:
                if isinstance(rec[key], dict) and rec[key].get('id') in objects:
                    rec[key] = objects[rec[key]['id']]
                elif rec[key] in objects:
                    rec[key] = objects[rec[key]]
                else:
                    rec[key] = None
