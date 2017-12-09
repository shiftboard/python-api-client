from result import Result, Results
from call import RPCServerError


class ProfileType(Result):
    name = 'profileType'
    name_plural = 'profile_types'


class ProfileTypes(Results):
    child = ProfileType


class ProfileData(Result):
    name = 'profileData'
    name_plural = 'profile_data'

    def updateProfileData(self):
        try:
            pd = self.copy()
            account = pd.pop('account')
            kwargs = {
                'account': account,
                'profile_data': [pd]
            }
            result = self.session.apicall('profileData.update', **kwargs)
            data = result['result']
        except RPCServerError as error:
            raise
        return data


class ProfileDataList(Results):
    child = ProfileData


class ProfileConfiguration(Result):
    name = 'profileConfiguration'
    name_plural = 'profile_configuration'


class ProfileConfigurationList(Results):
    child = ProfileConfiguration
