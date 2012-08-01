"""
Classes to represent a single workgroup or multiple workgroups (teams)
"""

from result import *

class Workgroup(Result):
    name = 'workgroup'
    name_plural = 'workgroups'

    def fullName(self):
        """To let us gloss over the difference between people and workgroups"""
        return self.get('name')


class Workgroups(Results):
    child = Workgroup
