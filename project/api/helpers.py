from tastypie.validation import Validation
from tastypie.resources import ModelResource
from tastypie.authentication import BasicAuthentication
from tastypie.exceptions import NotFound, ImmediateHttpResponse
from tastypie import http
from tastypie.utils.mime import determine_format, build_content_type
from tastypie.api import Api as TastypieApi
import json

class AuthenticationByMethod(BasicAuthentication):

    def __init__(self, *args, **kwargs):
        self.allowed_methods = list(args)
        super(AuthenticationByMethod, self).__init__()

    def is_authenticated(self, request, **kwargs):
        if request.user.is_authenticated() or request.method in self.allowed_methods:
            return True
        else:
            return super(AuthenticationByMethod, self).is_authenticated(request, **kwargs)


class ResourceExtension:
    
    @property
    def example_fields(self):
        example_fields = set()

        for method in ['POST','GET']:
            allowed = method.lower() in self._meta.allowed_methods
            if allowed:
                example_fields |= set(self._meta.examples[method].keys())
        example_fields.discard('resource_uri') 
        return example_fields


    def get_example_data(self,method):
        return dict(self._meta.examples[method])

    def sanitize_bundle(self, bundle, request=None):
        return 
        declared_fields = set(self.declared_fields.keys())
        request_fields = set(bundle.data.keys())
        for extra_field in (request_fields - declared_fields):
            del bundle.data[extra_field]

class ExtendedModelResource(ModelResource, ResourceExtension):

    def is_valid(self, bundle, request=None):
        #A little but hacky but we'll sanitize data every time we check if its valid
        self.sanitize_bundle(bundle, request)
        super(ExtendedModelResource, self).is_valid(bundle, request)
  
    def full_hydrate(self, bundle):
        try:
            bundle = super(ExtendedModelResource, self).full_hydrate(bundle)
        except NotFound, e:
            desired_format = self._meta.default_format 
            #TODO: use the actual serializer to send the error
            #serialized = self.serialize(None,
            #    json.dumps({'error' : e.message}), desired_format)
            response_dict = {'error' : e.message, 'error_code': "MISSING_RESOURCE"}
            response = http.HttpBadRequest(content=json.dumps(response_dict),
                    content_type=build_content_type(desired_format))

            raise ImmediateHttpResponse(response=response) 

        return bundle

    def create_test_resource(self, data={}):
        obj = self._meta.resource_class.create_test_model(data)
        bundle = self.build_bundle(obj=obj)
        location = self.get_resource_uri(bundle)
        return location, bundle.obj


class FieldsValidation(Validation):
    def __init__(self, required = [], validated = [], **kwargs ):
        all_methods = ['GET','POST','PUT','DELETE','PATCH']

        self.required_fields = {}
        self.validated_fields = {}

        dicts = {'required' : self.required_fields,
                 'validated' : self.validated_fields}

        self.map_method_validations(self.required_fields, required, all_methods)
        self.map_method_validations(self.validated_fields, validated, all_methods)

        for key, value in kwargs.items():
            for arr_name in ['required', 'validated']:
                if key[:len(arr_name)] == arr_name:
                    methods = self.parse_methods_key(key, arr_name)
                    self.map_method_validations(dicts[arr_name], value, methods)

        Validation.__init__(self)

    def parse_methods_key(self, key, prefix):
        prefix_len = len(prefix)+1 # prefix + underscore
        methods = key[prefix_len:].split('_')
        return [method.upper() for method in methods]


    def map_method_validations(self,target_dict, fields_to_add, methods):
        for method in methods:
            fields = target_dict.setdefault(method,[])
            for field in fields_to_add:
                fields.append(field)
        
    def is_valid(self, bundle, request):
        if not bundle.data:
            return {'__all__' : 'Missing data.'}

        required_errors = self.validate_required(bundle, request)
        validation_errors = self.validate_fields(bundle, request)

        errors = {}
        errors.update(required_errors)
        errors.update(validation_errors)

        return errors

    def validate_fields(self, bundle, request=None):
        errors = {}
        for field in self.validated_fields[request.method]:
            validation_func = getattr(self, '%s_is_valid' % field)
            if field in bundle.data:
                valid, reason = validation_func(bundle.data[field], bundle, request)
                if not valid:
                    errors[field] = reason
        return errors

    def validate_required(self, bundle, request=None):
        errors = {}
        for required_field in self.required_fields[request.method]:
            if required_field not in bundle.data:
                errors[required_field] = ['%s field is required.' % required_field]
        return errors


class Api:
    def __init__(self, resources):
        self.tastypieApi = TastypieApi(api_name='resources')
        self.dummy_resources = []
        self.resources = {}

        for resource_class in resources:
            resource = resource_class()
            self.resources[resource._meta.resource_name] = resource
            self.tastypieApi.register(resource)


    @property
    def urls(self):
        from django.conf.urls.defaults import url, patterns
        from dummy import DummyResource
        
        pattern_list =  []
        for resource_name, resource in self.resources.items():
            if resource_name in self.dummy_resources:
                pattern_list.append(
                    (r"^resources/%s/(\d*)/?$" % resource_name, DummyResource.get_view(resource)))

        urls = patterns("",*pattern_list)
        urls += self.tastypieApi.urls
        return urls

    def get_resource_list_uri(self, resource_name):
        return self.resources[resource_name].get_resource_list_uri()

    def get_resource_example_data(self, resource_name, method):
        return self.resources[resource_name].get_example_data(method)

    def resource_allows_method(self, resource_name, method):
        return method.lower() in self.resources[resource_name]._meta.allowed_methods


    def dehydrate(self,request, resource_name, obj):
        resource = self.resources[resource_name]
        bundle = resource.build_bundle(obj=obj, request=request)
        bundle = resource.full_dehydrate(bundle)
        return bundle.data
