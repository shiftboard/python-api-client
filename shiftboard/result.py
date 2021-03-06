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
                                    select={self.name: self['id']},
                                    extended=True,
                                    **self.reqargs
                                    )['result'][self.name_plural][0]

    def __hash__(self):
        return int(self['id'])

    def __eq__(self, other):
        return self.__class__ == other.__class__ and hash(self) == hash(other)

    def denormalizeReferenced(self, objects):
        """Denormalize, building lightweight versions of referenced data"""
        self.denormalizeLight(objects, 'timezone')
        self.denormalizeLight(objects, 'covering_member', 'account', cls=shiftboard.account.Account)
        self.denormalizeLight(objects, 'covering_workgroup', 'workgroup', cls=shiftboard.workgroup.Workgroup)
        self.denormalizeLight(objects, 'workgroup', cls=shiftboard.workgroup.Workgroup)
        self.denormalizeLight(objects, 'location', cls=shiftboard.location.Location)
        self.denormalizeLight(objects, 'work_status_type', 'workStatusType')
        self.denormalizeLight(objects, 'role', cls=shiftboard.role.Role)

    def denormalizeLight(self, objects, key, obj_name=None, cls=None):
        if not obj_name:
            obj_name = key
        if not obj_name in objects:
            return

        if key in self and self[key]:
            obj = objects[obj_name][self[key]]
            if cls:
                # higher level object
                self[key] = cls(self.session, seed=obj)
            else:
                # simple dict
                self[key] = obj


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
        try:
            start = obj['page']['this']['start'] - 1
        except:
            start = 0
        for obj in obj[self.child.name_plural]:
            self.storage[start] = self.element(obj)
            start += 1

    def getData(self, page={}):
        """Make the API call to get some data"""
        page['batch'] = self.batch
        return self.session.apicall('%s.list' % self.child.name,
                                    select=self.select,
                                    page=page,
                                    extended=True,
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
            if idx >= self.count:
                raise IndexError
            return self.storage[idx]
        except (KeyError, AttributeError):
            self.loadBatch(idx)
            try:
                return self.storage[idx]
            except (KeyError, AttributeError):
                return None

    def __iter__(self):
        for idx in range(0, len(self)):
            if idx >= len(self):
                # Why in the world is this happening???
                break
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
                select={selectkey: list(ids)},
                batch=shiftboard.MAX_BATCH_SIZE)
        )

        for rec in self:
            if key in rec and rec[key]:
                if isinstance(rec[key], dict) and rec[key].get('id') in objects:
                    rec[key] = objects[rec[key]['id']]
                elif rec[key] in objects:
                    rec[key] = objects[rec[key]]
                else:
                    rec[key] = None
