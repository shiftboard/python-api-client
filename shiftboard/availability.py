
from result import Result, Results

class Availability(Result):
    """Represents a single availability record"""
    name = 'availability'
    name_plural = 'availability'


class AvailabilityList(Results):
    """Represents multiple availability records"""
    child = Availability
