"""
Classes to represent single and multiple account records
"""

from result import *
from workgroup import Workgroup
from call import RPCServerError


class Account(Result):
    """Represents a single account record"""
    name = 'account'
    name_plural = 'accounts'

    def getData(self):
        # extended = True needed to get user_type (admin, etc.).
        result = self.session.apicall('account.get',
                                      id=self['id'],
                                      extended=True,
                                      org_settings=True,
                                      user_applications=True,
                                      )
        return result['result']

    def updateAccount(self):
        try:
            kwargs = self.copy()
            if 'default_language' in kwargs and kwargs['default_language'] == None:
                kwargs.pop('default_language', None)
            kwargs.pop('region', None)
            result = self.session.apicall('account.update', **kwargs)
            data = result['result']
        except RPCServerError as error:
            raise
        return data

    def delete(self):
        """Remove account"""
        try:
            result = self.session.apicall('account.delete', id=self['id'])
            return True
        except:
            return False

    def admin(self):
        """Returns true if user is a super-user"""
        return self.get('user_type', '') == 'admin'

    def workgroups(self):
        result = self.session.apicall('account.listMemberships',
                                      select={'member': self['id']}
                                      )
        data = result['result']['workgroups']
        return [Workgroup(self.session, seed=workgroup) for workgroup in data]

    def image(self):
        try:
            result = self.session.apicall('account.getImage', id=self['id'])
            data = result['result']['url']
        except RPCServerError as error:
            if error.code == "no_user_image":
                data = ""
            else:
                raise
        return data

    def fullName(self):
        return '%s %s' % (self.get('first_name', ''), self.get('last_name', ''))

    def __cmp__(self, other):
        return cmp('%s %s' % (self.get('last_name', ''), self.get('first_name', '')),
                   '%s %s' % (other.get('last_name', ''), other.get('first_name', '')))

    def __eq__(self, other):
        return other and self.get('id') == other.get('id')


class MyAccount(Account):
    """Represents my account"""

    def getData(self):
        # extended = True needed to get user_type (admin, etc.).
        result = self.session.apicall('account.self',
                                      extended=True,
                                      org_settings=True,
                                      user_applications=True,
                                      )
        return result['result']

    def user_applications(self):
        """Returns account's application permission set"""
        return self.get('user_applications')

    def onboard_labels_by_name(self):
        """Returns account's onboarding labels as dict with names as keys, integers as values"""
        labels = {}
        self.load()
        try:
            labelArray = self.get('org_settings').get('onboard_labels')
            for value in labelArray:
                labels[labelArray[value]] = value
        except:
            return labels
        return labels

    def onboard_labels(self):
        """Returns account's onboarding labels as dict with integers as keys, names as values"""
        self.load()
        try:
            labelArray = self.get('org_settings').get('onboard_labels')
        except:
            return {}
        return labelArray


class Accounts(Results):
    """Represents multiple Account records"""
    child = Account
