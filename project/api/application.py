from helpers import Api
from resources import UserProfileResource, MessageResource

class SecretApi(Api):

    def __init__(self):
        resources = [UserProfileResource, MessageResource]
        Api.__init__(self, resources)
