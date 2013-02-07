import unittest
import time

from django.test import TestCase
from django.conf import settings
from django.db import IntegrityError
from django.db import models
from django.test.utils import override_settings
from django.core.management import call_command
from django.db.models import loading
from django.contrib.contenttypes.models import ContentType

from icontact.models import IContact
from icontact.tests.models import MyContact
from icontact.adapter import IContactAdapter, IContactData
from icontact.observer import IContactObserver
from icontact.client import IContactClient, IContactException
    

class MyContactAdapter(IContactAdapter):

    def get_contact_data(self, instance):
        return IContactData(email=instance.email, first_name=instance.first_name)

class IContactObserverTests(TestCase):
    """
        iContact Custom Manager Tests
    """
    def setUp(self):
        settings.INSTALLED_APPS += ('icontact.tests',)
        loading.cache.loaded = False
        call_command('syncdb', verbosity=0)
        self.observer = IContactObserver()
        self.observer.observe(MyContact, MyContactAdapter())
        
    def tearDown(self):
        IContact.objects.all().delete()
        
    def test_client(self):
        self.assertIsInstance(self.observer.client(), IContactClient)
        
    def test_get_contact(self):
        contact = MyContact(email="victor35@rochapps.com")
        contact.save()
        contact = self.observer.get_contact(contact)
        self.assertTrue(contact)
        
    def test_create(self):
        contact = MyContact(email="victor36@rochapps.com")
        contact.save()
        local_icontacts = IContact.objects.all()
        self.assertTrue(local_icontacts)
        
    def test_update(self):
        contact = MyContact(email="victor37@rochapps.com")
        contact.save()
        contact.first_name = 'victor'
        contact.save() #should call the update method on the observer model
        contact = self.observer.get_contact(contact)
        contact_first_name = contact['contact']['firstName']
        self.assertEqual('victor', contact_first_name)
                
    def test_delete(self):
        contact = MyContact(email="victor38@rochapps.com")
        contact.save()
        time.sleep(10)
        icontact = self.observer.get_contact(contact)
        contact_id = icontact['contact']['contactId']
        contact.delete()
        client = self.observer.client()
        contact = client.get_contact(contact_id)
        self.assertEqual('deleted', contact['contact']['status'])
