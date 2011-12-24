"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.http import HttpRequest
from jsonrpc.proxy import ServiceProxy
from klooff.test import KlooffClient as Client
from klooff.test import MultiTestCase, create_multi_meta
from api.resources import UserProfileResource
from api.application import SecretApi as Api
from api.helpers import FieldsValidation
from api.models import UserProfile
from api.dummy import DummyResource, Dummy
from django.contrib.auth.models import User
import json


class FieldsValidationTest(TestCase):
    def test_parse_methods_key(self):
        validation = FieldsValidation()
        key = "required_post"
        #value = ['field1','field2']
        target = {}

        methods = validation.parse_methods_key(key,'required')
        self.assertEqual(['POST'], methods)

    def test_map_method_validation(self):
        validation = FieldsValidation()
        fields = ['field1','field2']
        methods = ["POST","PUT","GET","DELETE"]
        target = {}
        validation.map_method_validations(target, fields, methods)

        expected = {
                'POST' : ['field1','field2'],
                'GET' : ['field1','field2'],
                'PUT' : ['field1','field2'],
                'DELETE' : ['field1','field2'],
                }

        self.assertEqual(expected, target)

        validation.map_method_validations(target, ['field3'], ['PUT','POST'])

        expected = {
                'POST' : ['field1','field2','field3'],
                'GET' : ['field1','field2'],
                'PUT' : ['field1','field2','field3'],
                'DELETE' : ['field1','field2'],
                }

        self.assertEqual(expected, target)

    def test_fieldsvalidation_constructor(self):
        validation = FieldsValidation(required = ['f1','f2'],
                                      validated = ['f1','f3'],
                                      required_post_get = ['f4'],
                                      validated_put = ['f5'])

        expected_required = {
                'POST' : ['f1','f2','f4'],
                'GET' : ['f1','f2','f4'],
                'PUT' : ['f1','f2'],
                'DELETE' : ['f1','f2'],
                'PATCH' : ['f1','f2'],
                }

        expected_validated = {
                'POST' : ['f1','f3'],
                'GET' : ['f1','f3'],
                'PUT' : ['f1','f3','f5'],
                'DELETE' : ['f1','f3'],
                'PATCH' : ['f1','f3'],
                }

        self.assertEqual(expected_validated, validation.validated_fields)
        self.assertEqual(expected_required, validation.required_fields)

class UnderResources(MultiTestCase):

    @staticmethod
    def multi_create_test_resource(self, resource_name, resource):
        #only if resource allows detail GET
        if 'GET' not in resource._meta.detail_allowed_methods:
            return

        client = Client()
        msg = "Could not create test resource for %s" % resource_name

        try:
            resource.create_test_resource()
        except Exception, e:
            msg = "%s : %s - %s" % (msg, e.__class__.__name__, e.message)
            self.assertTrue(False,msg)

        get_response = client.get(resource.get_resource_list_uri(),parse='json')
        self.assertEqual(1,get_response.data['meta']['total_count'], msg)

    @staticmethod
    def multi_example_data(self, resource_name, resource):
        #Check existence
        client = Client()
        for method in ['POST', 'GET']:
            try:
                if self.api.resource_allows_method(resource_name, method):
                    get_example = resource._meta.examples[method]
            except (AttributeError, KeyError):
                message = "Missing example %s data for %s resource." 
                message %= (method, resource_name) 
                self.assertTrue(False,message)

        #Test POST
        if resource.can_create():
            post_response = client.post(resource.get_resource_list_uri(), 
                    resource.get_example_data('POST'))

            #TODO: find a better way to ignore missing resources on test
            if not post_response.content.startswith("Could not find the provided object via resource URI"):
                msg = "Failed to POST example data for resource '%s': %s" 
                msg %= (resource_name, post_response.content)
                self.assertEqual(post_response.status_code, 201, msg)

    @staticmethod
    def multi_example_get_data(self, resource_name, resource):
        #only if resource allows detail GET
        if 'GET' not in resource._meta.detail_allowed_methods:
            return

        client = Client()
        if self.api.resource_allows_method(resource_name, 'GET'):
            resource.create_test_resource() 
            get_response = client.get(resource.get_resource_list_uri())
            response_dict = json.loads(get_response.content)

            if len(response_dict['objects']) > 0:
                object_keys = set(response_dict['objects'][0].keys())
                expected_keys = set(resource._meta.examples['GET'].keys())

                msg = "GET example data does not match the example for resource %s - %s vs %s"
                msg %= (resource_name, expected_keys, object_keys)
                self.assertEqual(expected_keys, object_keys, msg)


    @staticmethod
    def multi_declared_example_fields_coherence(self, resource_name, resource):
        #only if resource allows detail GET
        if 'GET' not in resource._meta.detail_allowed_methods:
            return

        example_fields = set(resource.example_fields)
        declared_fields = set(resource.declared_fields.keys())

        delta = example_fields - declared_fields
        if len(delta) > 0:
            msg = "%s.%s field appears on the examples but is not declared."
            msg %= (resource_name,delta.pop())
            self.assertTrue(False, msg)
        
        delta = declared_fields - example_fields
        if len(delta) > 0:
            msg = "%s.%s field is declared but is missing from examples." 
            msg %= (resource_name,delta.pop())
            self.assertTrue(False, msg)

    @staticmethod
    def generate_arguments():
        api = Api()
        args = []
        for resource_name, resource in api.resources.items():
            args.append( (resource_name, resource) )
        return args

    @staticmethod
    def generate_test_name(resource_name, resource):
        return resource_name


class TestResources(TestCase):
    __metaclass__ = create_multi_meta(UnderResources)

    def setUp(self):
        self.api = Api()

class UnderResourceFields(MultiTestCase):

    @staticmethod
    def generate_field_test_data(field):
        field_classname = field.__class__.__name__ 
        if field_classname == 'CharField':
            bad_value = "abcd"
        elif field_classname == "IntegerField":
            bad_value = 12345

        return bad_value
        
    @staticmethod
    def multi_help(self, resource_name, resource, field_name, field):
        if field.help_text == field.__class__.help_text and field_name != 'resource_uri':
            msg = "Missing help text for %s.%s resource field."
            msg %= (resource_name, field_name)
            self.assertTrue(False,msg)
   
    @staticmethod
    def multi_readonly_post(self, resource_name, resource, field_name, field):
        client = Client()

        if field.readonly and resource.can_create() :
            post_data = resource.get_example_data('POST')
            
            bad_value = UnderResourceFields.generate_field_test_data(field)
            post_data[field_name] = bad_value

            post_response = client.post(resource.get_resource_list_uri(), post_data, parse='json')
            if post_response.status_code == 201:
                (prop, location) = post_response._headers['location']
                get_response = client.get(location, parse='json')
                msg = "%s.%s can be setted by a POST request even though it's readonly!."
                msg %= (resource_name, field_name)
                self.assertNotEqual(get_response.get(field_name,''), bad_value, msg)

    @staticmethod
    def multi_readonly_patch(self, resource_name, resource, field_name, field):
        client = Client()

        if field.readonly and resource.can_create() :
            #Create a resource to modify it
            (location, obj) = resource.create_test_resource()
            bad_value = UnderResourceFields.generate_field_test_data(field)

            #authenticate to be allowed to modify the resource
            post_data = resource.get_example_data('POST')
            client.login(username=post_data['email'], password=post_data['password'])

            #attempt to PATCH
            patch_data = {}
            patch_data[field_name] = bad_value
            patch_response = client.patch(location,patch_data, parse='json')
            get_response = client.get(location, parse='json')

            msg = "%s.%s can be changed by a PATCH request even though it's readonly!."
            msg %= (resource_name, field_name)
            self.assertNotEqual(get_response.data.get(field_name,None), bad_value,msg)

    @staticmethod
    def generate_arguments():
        api = Api()
        args = []
        for resource_name, resource in api.resources.items():
            for field_name, field in resource.fields.items():
                args.append( (resource_name, resource, field_name, field) )

        return args

    @staticmethod
    def generate_test_name(resource_name, resource, field_name, field):
        return "_".join([resource_name, field_name])



class TestResourceFields(TestCase):
    __metaclass__ = create_multi_meta(UnderResourceFields)

class TestDummy(TestCase):

    def test_get(self):
        user_res = UserProfileResource()
        dummy_res = DummyResource(user_res)
        request = HttpRequest()
        request.method="GET"

        response = dummy_res.get(request,1)
        self.assertEqual(200, response.status_code)
        self.assertEqual(user_res._meta.examples['GET'], json.loads(response.content))

    def test_post(self):
        user_res = UserProfileResource()
        dummy_res = DummyResource(user_res)
        request = Dummy()
        request.method="POST"
        request.raw_post_data = json.dumps(user_res._meta.examples['POST'])
        request.path = "/api/resources/userprofile/"

        response = dummy_res.post(request)
        self.assertEqual(201, response.status_code)
        self.assertEqual("",response.content)


class TestUserProfile(TestCase):
    def setUp(self):
        self.client = Client()
        self.api = Api()
        self.users_list_url = self.api.get_resource_list_uri('userprofile')
        self.user_post_data = self.api.get_resource_example_data('userprofile','POST')

    def test_basic_operations(self):
        user_data = {
            "username":"godinez5",
            "password":"mypassword",
            "email" : "juanelo@godinez.cl"
        }

        #Create a userprofile
        user=User.objects.create_user(**user_data)
        profile = UserProfile(user=user, facebook_id=31337)
       
        profile.username = "jia200x"
        #Set some properties
        patch = {"facebook_id":666}
        profile.set(**patch)

        #Get them, and check if they are returned
        self.assertEqual(profile.username,"jia200x")
        self.assertEqual(profile.user.username,"jia200x")
        self.assertEqual(profile.facebook_id,666)

    def test_get(self):
        user = User.objects.create_user(username="test1",
            email="test@test.tes", password="123456")
        user.save()
        profile = UserProfile.get(user)
        self.assertEqual('test1', profile.username)

    def test_missing_email(self):
        del self.user_post_data['email']
        post_response = self.client.post(self.users_list_url, 
            self.user_post_data, parse='json')
        self.assertEqual(400, post_response.status_code) # 400: CLIENT ERROR
        self.assertEqual(['email'], post_response.data.keys())

    def test_missing_password(self):
        del self.user_post_data['password']
        post_response = self.client.post(self.users_list_url, 
                self.user_post_data, parse='json')
        self.assertEqual(400, post_response.status_code) # 400: CLIENT ERROR
        self.assertEqual(['password'], post_response.data.keys())

    def test_change_password(self):
        client = self.client
        old_password = "OLDKGAS$AFAG"
        new_password = "NEWHSXC41A$A" 

        #obtain a test user profile
        (location, profile) = self.api.resources['userprofile'].create_test_resource({'password' : old_password})
        #login with the profile
        self.assertTrue(client.login(username=profile.email, password=old_password))

        #change password patch
        patch_data = { "password" : new_password }
        response = client.patch(location, patch_data)

        #Attempt with new password
        self.assertEqual(202, response.status_code, response.content)
        #Try to login again with old password
        client.logout()
        self.assertFalse(client.login(username=profile.email, password=old_password))
        #Try with the new one
        self.assertTrue(client.login(username=profile.email, password=new_password))

    def test_resource(self):
        client = self.client

        #test POST
        post_response = client.post(self.users_list_url, self.user_post_data)
        self.assertEqual(post_response.status_code, 201, post_response.content)

        #test matching GET
        get_response = client.get(self.users_list_url, parse='json')
        self.assertEqual(get_response.status_code, 200, get_response.content)

        userprofile_dict = get_response.data['objects'][0]
        userprofile_keys = userprofile_dict.keys()

        self.assertTrue('email' in userprofile_keys)
        self.assertTrue('facebook_id' in userprofile_keys)

        #test attempt unauthorized put
        put_data = dict(self.user_post_data)
        put_data['first_name'] = "darth"
        put_response = client.put(userprofile_dict['resource_uri'],put_data)
        self.assertEqual(put_response.status_code, 401, put_response.content) #UNAUTHORIZED

        #test authenticate
        rpc_response = client.rpc('authenticate', 
            email=self.user_post_data['email'], password=self.user_post_data['password'])
        self.assertEqual(200,rpc_response.status_code, rpc_response.content)

        #test PUT
        put_data = self.user_post_data
        put_data['first_name'] = "darth"
        put_response = client.put(userprofile_dict['resource_uri'], put_data)

        self.assertEqual(put_response.status_code, 204, put_response.content)

        #test PATCH
        patch_data = dict(put_data)
        patch_response = client.patch(userprofile_dict['resource_uri'], {'last_name':'vader'})
        self.assertEqual(patch_response.status_code, 202, patch_response.content)

        #test PATCH to superuser (not allowed)
        patch_data = {'is_superuser': True, 'is_staff' : True}
        patch_response = client.patch(userprofile_dict['resource_uri'], patch_data)
        user_id = int(userprofile_dict['resource_uri'].split('/')[-2])
        user = User.objects.get(id=user_id)
        self.assertFalse(user.is_superuser,"Allowed user to made himself superuser!")
        self.assertFalse(user.is_staff,"Allowed user to made himself staff!")

        #test PATCH to facebook_id (not allowed)
        patch_data = {'facebook_id' : 12345678}
        patch_response = client.patch(userprofile_dict['resource_uri'], patch_data)
        user_id = int(userprofile_dict['resource_uri'].split('/')[-2])
        user = User.objects.get(id=user_id)
        profile = UserProfile.get(user)
        self.assertNotEqual(12345678,profile.facebook_id,"Allowed user to change his own facebook_id by POST/PUT!")

        #test matching GET
        get_response = client.get(userprofile_dict['resource_uri'], parse='json')
        userprofile_dict = get_response.data
        expected_data = dict(put_data)
        del expected_data['password']
        expected_data['last_name'] = 'vader'

        self.assertEqual(get_response.status_code, 200, get_response.content)
        self.assertDictContainsSubset(expected_data, userprofile_dict)

