"""
Classes to represent single and multiple shifts.
"""
import time, datetime

from result import *
from workgroup import Workgroups, Workgroup
from account import Accounts, Account
from shift import Shift

TIMEFMT = '%l:%M%P'

class Timeclock(Result):
    """Represents a single timeclock entry"""

    name = 'timeclock'
    name_plural = 'timeclocks'

    def __init__(self, session, seed=None, id=None):
        self.session = session
        self.loaded = False

        if seed:
            self.update(seed)

        if id:
            self['id'] = id
            self.load()

        if (not 'id' in self):
            self['id'] = self['account']


    def getData(self):
        result = self.session.apicall('timeclock.status',
            account = self['id']
            )
        return result['result']

    def time(self, show_end_time=False, timefmt=TIMEFMT):
        """Human-readable time display"""
        start_time = self.startTime()
        if 'clocked_out' in self and show_end_time:
            return '%s - %s' % (
                start_time.strftime(timefmt),
                self.endTime().strftime(timefmt),
                )
        if start_time.date() != datetime.date.today():
            return '%s' % (self.startTime().strftime(timefmt+" (%B %d, %Y)"),)

        return '%s' % (self.startTime().strftime(timefmt),)

    def startTime(self):
        """parse clock in time into standard python structure"""
        if 'clocked_in_local' in self:
            timeobj = datetime.datetime.strptime(
                self['clocked_in_local'], '%Y-%m-%dT%H:%M:%S')
        else:
            # Standard clockin specified in UTC time
            clockin_str = self['clocked_in']
            clockin_str = clockin_str.rstrip("Z")
            clockin_time = datetime.datetime.strptime(
                clockin_str, '%Y-%m-%dT%H:%M:%S')
            utctzdiff = datetime.datetime.utcnow() - datetime.datetime.now()
            timeobj = clockin_time - utctzdiff
        return timeobj

    def endTime(self):
        """parse clock out time into standard python structure"""
        if 'clocked_out_local' in self:
            timeobj = datetime.datetime.strptime(
                self['clocked_out_local'], '%Y-%m-%dT%H:%M:%S')
        else:
            # Standard clockin specified in UTC time
            clockout_str = self['clocked_out']
            clockout_str = clockin_str.rstrip("Z")
            clockout_time = datetime.datetime.strptime(
                clockout_str, '%Y-%m-%dT%H:%M:%S')
            utctzdiff = datetime.datetime.utcnow() - datetime.datetime.now()
            timeobj = clockout_time - utctzdiff
        return timeobj

    def clockedin(self):
        """Boolean test for checked in status"""
        if self.get('clocked_in', False) and not self.get('clocked_out', False):
            return True

        return False

    def clockIn(self, account=None, workgroup=None, shift=None):
        """Clock in the current timeclock object"""
        if (not account and 'account' in self):
            account = self['account']
        if (not workgroup and 'workgroup' in self):
            workgroup = self['workgroup']
        if (not shift and 'shift' in self):
            shift = self['shift']

        arglist = { 'account': account }

        if (workgroup):
            arglist['workgroup'] = workgroup

        if (shift):
            arglist['shift'] = shift

        result = self.session.apicall('timeclock.clockIn', **arglist)
        return result['result']

    def clockOut(self, account=None, workgroup=None, approve=True):
        """Clock out of the current timeclock object"""
        if (not workgroup and 'workgroup' in self):
            workgroup = self['workgroup']
        if (not account and 'account' in self):
            account = self['account']

        arglist = { 'account': account }

        if (workgroup):
            arglist['workgroup'] = workgroup

        result = self.session.apicall('timeclock.clockOut',
            account = account,
            workgroup = workgroup,
            approve = approve,
            )
        return result['result']

    def __cmp__(self, other):
        # use string comparison to optimize..
        delta = cmp(self.get('id',''), other.get('id',''))
        if delta:
            return delta

        delta = cmp(self.get('clocked_in',''), other.get('clocked_in',''))
        if delta:
            return delta

        delta = cmp(self.get('clocked_out',''), other.get('clocked_out',''))
        if delta:
            return delta

        delta = cmp(self.get('account',''), other.get('account', ''))
        if delta:
            return delta

        delta = cmp(self.get('workgroup',''), other.get('workgroup', ''))
        if delta:
            return delta

        delta = cmp(self.get('shift',''), other.get('shift', ''))
        if delta:
            return delta

        return delta

    def __ne__(self, other):
        return not (self == other)

    def __eq__(self, other):
        return (self['id'] == other['id'] and 
                self['clocked_in'] == other['clocked_in'] and
                self.get('clocked_out') == other.get('clocked_out') and
                self['workgroup']['id'] == other['workgroup']['id'] and
                self['account']['id'] == other['account']['id'] and
                self['shift']['id'] == other['shift']['id'])

    def denormalizeReferenced(self, objects):
        """Denormalize, building lightweight versions of referenced data"""
        self.denormalizeBatch(objects, 'timezone')
        self.denormalizeBatch(objects, 'account', cls=Account)
        self.denormalizeBatch(objects, 'workgroup', cls=Workgroup)

    def denormalizeBatch(self, objects, key, obj_name=None, cls=None):
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


class WhosOnTimeclocks(Results):
    """Represents a list of timeclocks"""
    child = Timeclock

    def getData(self, page={}):
        page['batch'] = self.batch
        result = self.session.apicall('timeclock.whosOn',
            extended=True, select=self.select, page=page)
        return result

    def storeBatch(self, obj):
        Results.storeBatch(self, obj)
        if 'referenced_objects' in obj and int(obj['count']) > 0:
            referenced_objs = obj['referenced_objects']

            # index objects by most likely unique key
            objidx = dict()
            for referenced_name, referenced_list in referenced_objs.iteritems():
                for referenced_obj in referenced_list:
                    if 'id' in referenced_obj:
                        objidx.setdefault(referenced_name, dict())[referenced_obj['id']] = referenced_obj
                    elif 'name' in referenced_obj:
                        objidx.setdefault(referenced_name, dict())[referenced_obj['name']] = referenced_obj
            start = obj['page']['this']['start'] - 1
            for idx in range(start, start + len(obj[self.child.name_plural])):
                self.storage[idx].denormalizeReferenced(objidx)
