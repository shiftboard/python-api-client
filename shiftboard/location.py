"""
Classes to represent a single location or multiple locations
"""
from result import *

class Location(Result):
    """Represents a single location"""
    name = 'location'
    name_plural = 'locations'

class Locations(Results):
    """Represents multiple locations"""
    child = Location
