
from result import Result, Results

class Role(Result):
    """Represents a single role"""
    name = 'role'
    name_plural = 'roles'


class Roles(Results):
    """Represents multiple roles"""
    child = Role
