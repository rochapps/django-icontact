import datetime
import unittest
import requests
import json

from django.conf import settings
from django.contrib.auth.models import User
from django.core import mail
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import RequestFactory

from icontact.client import IcontactClient
from icontact.client import IcontactException

class IcontactClientTests(TestCase):
    """
        Tests for the Icontact Client
    """
    
    def setUp(self):
        self._client = IcontactClient()
        self.data = {"email": "victor@rochapps.com"}
        self.create_data = {'contact':{"email":"info@rochapps.com"}}
        
    def test_get_headers(self):
        headers = self._client._get_headers()
        self.assertEqual(6, len(headers))
        needed_headers = ['Accept', 'Content-Type', 'Api-Version', 'App-AppId',
            'Api-Username', 'API-PASSWORD']
        for header in headers:
            self.assertIn(header, headers)
        self.assertNotIn('Crazy-header', headers) 
        self.assertIsInstance(headers, dict)
        
    def test_prepare_url(self):
        baseurl = settings.ICONTACT_URL
        account_id = 123456
        folder_id = 1234
        resource_url = 'contacts/'
        client = IcontactClient(folder_id=folder_id, account_id=account_id)
        url = client.prepare_url(resource_url=resource_url)
        self.assertEqual(
            'https://app.sandbox.icontact.com/icp/a/123456/c/1234/contacts/',
            url)
            
    def test_process_response(self):
        #lets try it out with an real url
        url = self._client.prepare_url(resource_url='contacts/')
        r = requests.get(url, headers=self._client._get_headers())
        json_response = self._client.process_response(r)
        self.assertIsInstance(json_response, dict)
        #accesing a resource that doent exists should rise an error
        url = self._client.prepare_url(resource_url='contacts/1/')
        r = requests.get(url, headers=self._client._get_headers())
        self.assertRaises(IcontactException, self._client.process_response, r)
        #accesing crazy url should raise exception
        url = self._client.prepare_url(resource_url='contactus/1/')
        r = requests.get(url, headers=self._client._get_headers())
        self.assertRaises(IcontactException, self._client.process_response, r)
        
    def test_create_contact(self):
        client = self._client
        r = client.create_contact(payload=self.create_data)
        contact = r['contacts'][0]
        self.assertEqual('info@rochapps.com', contact['email'])
        self.assertTrue(contact['contactId'])
        #it would rise an exception to created a client without the required
        #email or with bad formatting
        data = {'contact':{"email":""}}
        self.assertRaises(IcontactException, client.create_contact,
            payload=data)
        
    def test_get_contacts(self):
        client = self._client
        r = client.get_contacts()
        self.assertIsInstance(r, dict)
        total = r['total']
        contacts = r['contacts']
        self.assertEqual(total, len(contacts))

    #TODO: find a way around this
    @unittest.skip("""icontact keeps old data and this function doesnt 
        work properly""")
    def test_update_contact(self):
        client = self._client
        r = client.create_contact(payload=self.create_data)
        contact = r['contacts'][0]
        contactId = contact['contactId']
        self.assertEqual('info@rochapps.com', contact['email'])
        r = client.update_contact(contactId=contactId, payload=self.data)
        contact = r['contact']
        self.assertEqual(contact['email'], self.data['email'])

    def test_get_contact(self):
        client = self._client
        #lets create a client to retrive it
        r = client.create_contact(payload=self.create_data)
        contact = r['contacts'][0]
        contactId = contact['contactId']
        self.assertEqual('info@rochapps.com', contact['email'])
        #retriving client
        r = client.get_contact(contactId)
        new_contact = r['contact']
        self.assertEqual('info@rochapps.com', contact['email'])
        new_contactId = new_contact['contactId']
        self.assertEqual(contactId, new_contactId)
        #retriving a client that doesn't exists should rise an exception
        self.assertRaises(IcontactException, client.get_contact, 23)
        
    def test_delete_contact(self):
        client = self._client
        #create contact
        r = client.create_contact(payload=self.create_data)
        contact = r['contacts'][0]
        contactId = contact['contactId']
        #delete contact
        r = client.delete_contact(contactId=contactId)
        self.assertFalse(len(r))
        #deleting client that doesnt exists raises exception
        self.assertRaises(IcontactException, client.delete_contact, contactId)        

    def test_subscription(self):
        client = self._client
        r = client.create_contact(payload=self.create_data)
        contact = r['contacts'][0]
        contactId = contact['contactId']
        subs = client.subscribe(contactId=contactId)
        num_subscribtions = len(subs)
        self.assertIn('subscriptions', subs)
        #subscribing again raises an exception
        self.assertRaises(IcontactException, client.subscribe, contactId)
