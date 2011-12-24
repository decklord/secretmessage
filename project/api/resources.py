from django.contrib.auth.models import User
from tastypie.bundle import Bundle
from tastypie.authorization import Authorization, DjangoAuthorization
from tastypie import fields
from api.helpers import FieldsValidation, AuthenticationByMethod
from api.helpers import ExtendedModelResource as ModelResource
from models import UserProfile, Message
from tastypie.authorization import Authorization
import settings

from datetime import datetime, timedelta

class MessageResource(ModelResource):

    description = fields.CharField(attribute='description', help_text='A public description of the message')
    message = fields.CharField(attribute='message', help_text='The hidden messsage.')
    time_to_reveal = fields.DateField(help_text='Time in seconds until reveal.')
    code = fields.CharField(attribute='code', readonly=True, help_text="The public code to id the message")
    admin_code = fields.CharField(attribute='admin_code', help_text="A private code to enter the message admin page.")


    class Meta:
        queryset = Message.objects.all()
        authorization = Authorization()
        excludes = ['opened','readed','id', 'reveal_on']
        resource_class = Message
        examples = {
                'POST' : {
                    'description' : 'bla bla',
                    'message' : 'el mensaje',
                    'time_to_reveal' : 4000,
                },
                'GET' : {
                    'description' : 'bla bla',
                    'message' : 'el mensaje',
                    'time_to_reveal' : 4000,
                    'code' : 'HGFSCVZSA2B',
                    'resource_id' : '/api/resources/message/1/',
                }
            }

    def obj_update(self, bundle, request=None, **kwargs):
        try:
            del bundle.data['admin_code']
        except KeyError:
            pass
        return super(MessageResource, self).obj_update(bundle, request, **kwargs)

    def hydrate_time_to_reveal(self, bundle):
        now = datetime.now()
        ttr = int(bundle.data['time_to_reveal'])
        delta = timedelta(seconds=ttr)
        bundle.obj.reveal_on = now + delta
        return bundle

    def full_dehydrate(self, bundle):
        bundle = super(MessageResource, self).full_dehydrate(bundle)
        now = datetime.now()
        if bundle.obj.reveal_on > now:
            bundle.data['message'] = ""
        del bundle.data['admin_code']

        revealDate =  bundle.obj.reveal_on
        now = datetime.now()
        if now > revealDate:
            bundle.data['time_to_reveal'] = 0
        else :
            delta = revealDate - now
            bundle.data['time_to_reveal'] = delta.seconds
        return bundle


class UserProfileValidation(FieldsValidation):

    def __init__(self):
        super(UserProfileValidation, self).__init__(
                required=['first_name', 'last_name'],
                validated=['email'],
                required_post=['email', 'password'],
                validated_post=['password'],
        )

    def save(self):
        self.user.save()
        self.profile.save()

    @staticmethod
    def password_is_valid(password, bundle, request):
        if len(password) < 6:
            return False, 'Password is too short.'
        return True, ""

    @staticmethod
    def email_is_valid(email, bundle, request):
        try:
            username = email
            #email is also username
            user = User.objects.get(username=username)

            is_post = request.method == "POST"
            is_put = request.method == "PUT"
            user_exists = user is not None
            invalid_post = user_exists and is_post
            same_user = user.id == request.user.id
            invalid_put = user_exists and is_put and not same_user

            if invalid_post or invalid_put:
                msg = "The username is already taken. %s %s %s"
                msg %= (user, request.method, request.user)
                return False, msg

        except User.DoesNotExist:
            return True, ""
        return True, ""


class UserProfileResource(ModelResource):
    first_name = fields.CharField(attribute='first_name',
        help_text='Real first name of the user (not a nickname).')
    last_name = fields.CharField(attribute='last_name',
        help_text='Real last name of the user.')
    email = fields.CharField(attribute='email',
        help_text='''Has to be a valid email. Will also be used as the username for login.''')
    facebook_id = fields.IntegerField(attribute='facebook_id', null=True, blank=True,
        help_text='Facebook id of the user. Should not be sent on POST.', readonly=True)
    password = fields.CharField(
        help_text='User password when creating a new one on POST or when changing it on PUT/PATCH.')

    class Meta:
        resource_name = 'userprofile'
        authorization = Authorization()
        authentication = AuthenticationByMethod("POST", "GET")
        validation = UserProfileValidation()

        object_class = UserProfile
        queryset = UserProfile.objects.all()

        allowed_methods = ['get', 'post', 'put', 'patch']
        excludes = ['is_superuser', 'is_staff', 'is_active', 'id', 'username']
        examples = {
                'POST': {
                     "first_name":  "Juan",
                     "last_name":  "Munoz",
                     "email":  "juanique@gmail.com",
                     "password":  "123456",
                },
                'GET': {
                    "first_name":  "Juan",
                    "last_name":  "Munoz",
                    "email":  "juanique@gmail.com",
                    "facebook_id":  "34523419",
                    "resource_uri":  "/api/resources/userprofile/1/",
                }
        }

    def create_test_resource(self, forced_data={}):
        data = self.get_example_data('POST')
        data.update(forced_data)
        bundle = self.build_bundle(data=data)
        bundle = self.obj_create(bundle=bundle)
        location = self.get_resource_uri(bundle)
        return location, bundle.obj

    def get_resource_uri(self, bundle_or_obj):
        kwargs = {}
        kwargs['resource_name'] = self._meta.resource_name
        if isinstance(bundle_or_obj, Bundle):
            kwargs['pk'] = bundle_or_obj.obj.id
        else:
            kwargs['pk'] = bundle_or_obj.id
        if self._meta.api_name is not None:
            kwargs['api_name'] = self._meta.api_name

        return self._build_reverse_url("api_dispatch_detail", kwargs=kwargs)

    def full_dehydrate(self, bundle):
        bundle = super(UserProfileResource, self).full_dehydrate(bundle)
        del bundle.data['password']
        return bundle

    def hydrate_password(self, bundle):
        try:
            bundle.obj.set_password(bundle.data['password'])
        except KeyError, e:
            pass

        return bundle

    def obj_create(self, bundle, request=None, **kwargs):
        create_data = {'username': bundle.data['email'],
                        'email': bundle.data['email'],
                        'password': bundle.data['password']}

        user = User.objects.create_user(**create_data)
        profile = UserProfile(user=user)

        userprofile_data = {
            'is_staff': False,
            'is_active': True,
            'is_superuser': False,
        }

        profile.set(**userprofile_data)

        bundle.obj = profile
        bundle = self.full_hydrate(bundle)

        profile.save()

        return bundle

    def obj_update(self, bundle, request=None, **kwargs):
        bundle.obj = self.obj_get(request=request, **kwargs)
        try:
            bundle.data['username'] = bundle.data['email']
        except:
            pass

        bundle = self.full_hydrate(bundle)
        bundle.obj.save()
