class UserProfileDoesNotExist(Exception):
    def __init__(self):
        self.value = "User profile does not exist for the given user"
    def __str__(self):
        return repr(self.value)
