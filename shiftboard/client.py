
from result import Result, Results

class Client(Result):
    """Represents a single client"""
    name = 'client'
    name_plural = 'clients'


class Clients(Results):
    """Represents multiple clients"""
    child = Client
