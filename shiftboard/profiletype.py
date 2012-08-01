
from result import Result, Results

class ProfileType(Result):
      name='profileType'
      name_plural='profile_types'

class ProfileTypes(Results):
      child=ProfileType
