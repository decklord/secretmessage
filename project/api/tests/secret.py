from django.test import TestCase
from klooff.test import KlooffClient as Client
from api.application import SecretApi as Api

class SecretTest(TestCase):
    def test_change_admin_code(self):
        api = Api()
        client = Client()

        (location, obj) = api.resources['message'].create_test_resource()
        old_code = obj.admin_code
        new_code = "GDFGACVAS"
        patch_data = { "admin_code" :  new_code }
        response = client.patch(location, patch_data, parse='json')
        obj = obj.__class__.objects.get(id=obj.id)
        self.assertEqual(old_code, obj.admin_code)

        print location

    def test_dehydrate(self):
        api = Api()
        msg_uri = api.resources['message'].get_resource_list_uri()
        client = Client()
        future_data = {
            'description' : 'soy una descripcion',
            'message' : 'yo no deberia estar aca',
            'time_to_reveal' : 6000,
            'admin_code' : "ASDSAAFA",
        }
        past_data = {
            'description' : 'soy una descripcion',
            'message' : 'yo si',
            'time_to_reveal' : -6000,
            'admin_code' : "ASDSAAFA",
        }

        response = client.post(msg_uri, future_data, parse='json')
        self.assertEqual(201, response.status_code, response.content)
        future_uri = response._headers['location'][1]

        response = client.post(msg_uri, past_data, parse='json')
        self.assertEqual(201, response.status_code, response.content)
        past_uri = response._headers['location'][1]

        response = client.get(past_uri, parse='json')
        self.assertTrue( 'code' in response.data.keys() and len(response.data['code']) )
        self.assertTrue( 'admin_code' not in response.data.keys())
        self.assertEqual(200, response.status_code, response.content)
        self.assertEqual(past_data['message'], response.data['message'])

        response = client.get(future_uri, parse='json')
        self.assertEqual(200, response.status_code)
        self.assertTrue( 'code' in response.data.keys() and len(response.data['code']) )
        self.assertEqual("",response.data['message'])
