"""
Classes to represent single and multiple shifts.
"""
import time, datetime

from result import *
from workgroup import Workgroups, Workgroup
from account import Accounts, Account
from location import Locations, Location
from role import Roles, Role
from profiletype import ProfileTypes

TIMEFMT = '%l:%M%P'
DAYFMT = '%B %d, %Y'

class Shift(Result):
    """Represents a single shift"""

    name = 'shift'
    name_plural = 'shifts'

    def getData(self):
        """Fetch one shift from the API"""
        result = self.session.apicall('shift.get',
            id = self['id']
            )
        return result['result']['shift']

    def time(self, show_end_date=True, timefmt=TIMEFMT):
        """Human-readable time display"""
        # todo: handle ending on a different day?
        if self.allDay():
            return '(All Day)'
        if 'end_date' in self and show_end_date:
            return '%s - %s' % (
                self.startDate().strftime(timefmt),
                self.endDate().strftime(timefmt),
                )

        return '%s' % (self.startDate().strftime(timefmt),)

    def day(self, show_end_date=True, dayfmt=DAYFMT):
        """Human-readable day display"""
        start_date = self.startDate()

	if start_date.date() == datetime.date.today():
            return 'Today'

        if 'end_date' in self and show_end_date:
            end_date = self.endDate()
            if (end_date.date() != start_date.date()):
                return '%s - %s' % (
                    start_date.strftime(dayfmt),
                    end_date.strftime(dayfmt),
                    )

        return '%s' % (start_date.strftime(dayfmt),)

    def allDay(self):
        try:
            datetime.datetime.strptime(
                self['start_date'], '%Y-%m-%dT%H:%M:%S')
            return False
        except ValueError: # all-day events have no start time
            return True

    def startDate(self):
        """parse start date into standard python structure"""
        try:
            return datetime.datetime.strptime(
                self['start_date'], '%Y-%m-%dT%H:%M:%S')
        except ValueError: # all-day events have no start time
            return datetime.datetime.strptime(
                self['start_date'], '%Y-%m-%d')

    def endDate(self):
        try:
            return datetime.datetime.strptime(
                self['end_date'], '%Y-%m-%dT%H:%M:%S')
        except KeyError:
            return None

    def workgroupName(self):
        return (
            self.get('workgroup') or
            { 'name': '[ no workgroup ]' }
            ).get('name')

    def locationName(self):
        """Get the location name, expects it to be denormalized."""
        return (
            self.get('location') or
            { 'name': '[ no location specified ]' }
            ).get('name')

    def coveredBy(self):
        """
        Shortcut to retrive either the covering_member or covering_workgroup
        """
        return self.get('covering_member', self.get('covering_workgroup'))

    def __str__(self):
        return '%s %s' % (self.time(), self.get('subject', ''))

    def __cmp__(self, other):
        # use string comparison to optimize..
        delta = cmp(self.get('start_date'), other.get('start_date'))
        if delta:
            return delta

        if 'end_date' in self and 'end_date' in other:
            delta = cmp(self.get('end_date'), other.get('end_date'))
        # shift with no end date is "greater" than one with
        elif 'end_date' in self:
            delta = -1
        elif 'end_date' in other:
            delta = 1
        else:
            delta = 0
        if delta:
            return delta

        delta = cmp(self.get('subject',''), other.get('subject',''))
        if delta:
            return delta

        delta = cmp(self.get('id',''), other.get('id',''))
        if delta:
            return delta

        delta = cmp(self.get('workgroup',''), other.get('workgroup', ''))
        if delta:
            return delta

        return delta

    def __ne__(self, other):
        return not (self == other)

    def __eq__(self, other):
        return (self['start_date'] == other['start_date'] and
                self.get('end_date') == other.get('end_date') and
                self['workgroup']['id'] == other['workgroup']['id'] and
                self.get('subject') == other.get('subject') and
                self.get('covered') == other.get('covered') and
                self.get('covering_member', '') == other.get('covering_member'))

    def denormalizeReferenced(self, objects):
        """Denormalize, building lightweight versions of referenced data"""
        self.denormalizeLight(objects, 'timezone')
        self.denormalizeLight(objects, 'covering_member', 'account', cls=Account)
        self.denormalizeLight(objects, 'covering_workgroup', 'workgroup', cls=Workgroup)
        self.denormalizeLight(objects, 'workgroup', cls=Workgroup)
        self.denormalizeLight(objects, 'location', cls=Location)
        self.denormalizeLight(objects, 'work_status_type', 'workStatusType')
        self.denormalizeLight(objects, 'role', cls=Role)

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


class Shifts(Results):
    """Represents a list of shifts"""
    child = Shift

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

    def denormalizeWorkgroups(self):
        self.denormalize(Workgroups)

    def denormalizeAccounts(self):
        self.denormalize(Accounts, key='covering_member')

    def denormalizeLocations(self):
        self.denormalize(Locations)

    def denormalizeRoles(self):
        self.denormalize(Roles)

    def denormalizeProfileTypes(self):
        """
        Replace profile_type ids with objects in covering_member.
        Expects covering_member to be denormalized.
        """

        profiles = ProfileTypes(
            self.session,
            batch = shiftboard.MAX_BATCH_SIZE,
            )

        profiled = dict((p['id'], p) for p in profiles)

        for shift in self:
            member = shift.get('covering_member')
            if member:
                # present and not already dereferenced:
                if isinstance(member.get('profile_type'), str):
                    member['profile_type'] = profiled[member['profile_type']]


class ExtendedShifts(Shifts):
    """Represents a list of shifts having an extended attribute list"""

    def getData(self, page={}):
        page['batch'] = self.batch
        return self.session.apicall('shift.list',
            extended=True, select=self.select, page=page)

class WhosOnShifts(Shifts):
    """Represents a list of shifts scheduled right now"""

    def getData(self, page={}):
        page['batch'] = self.batch
        return self.session.apicall('shift.whosOn',
            select=self.select, page=page)

    def denormalizeTimeclocks(self):
        for shift in self:
            member = shift.get('covering_member')
            if member:
                account_id = member.get('id')
                if account_id:
                    shift['timeclock'] = self.session.Timeclock(id=account_id)
