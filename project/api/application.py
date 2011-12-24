from helpers import Api
from resources import UserProfileResource

class SecretApi(Api):

    def __init__(self):
        resources = [UserProfileResource]
        Api.__init__(self, resources)
