from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from jsonrpc import jsonrpc_method
from jsonrpc.exceptions import Error
from api.application import SecretApi as Api
from models import UserProfile

api = Api()

class ClientError(Error):
    status = 400

class WrongPassword(ClientError):
    message = "Incorrect username/password combination."

class InactiveUser(ClientError):
    message = "User is not active."


@jsonrpc_method('authenticate(String, String) -> Object', validate=True)
def authenticate_user(request, email, password):
    username = email
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            return api.dehydrate(request=request,resource_name='userprofile',obj=UserProfile.get(user))
        else:
            raise InactiveUser()
    else:
        raise WrongPassword()


@jsonrpc_method('echo()')
def echo(request, *args,**kwargs):
    if len(args) > 0:
        return ''.join(args)
    return kwargs
