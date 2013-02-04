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

from icontact.models import iContact
from icontact.tests.models import MyContact
from icontact.adapter import iContactAdapter, iContactData
from icontact.observer import iContactObserver
from icontact.client import IcontactClient, IcontactException
    

class MyContactAdapter(iContactAdapter):

    def get_contact_data(self, instance):
        return iContactData(email=instance.email, firstName=instance.firstName)

class iContactObserverTests(TestCase):
    """
        iContact Custom Manager Tests
    """
    def setUp(self):
        settings.INSTALLED_APPS += ('icontact.tests',)
        loading.cache.loaded = False
        call_command('syncdb', verbosity=0)
        self.observer = iContactObserver()
        self.observer.observe(MyContact, MyContactAdapter())
        
    def tearDown(self):
        iContact.objects.all().delete()
        
    def test_client(self):
        self.assertIsInstance(self.observer.client(), IcontactClient)
        
    def test_get_contact(self):
        contact = MyContact(email="victor5@rochapps.com")
        contact.save()
        contact = self.observer.get_contact(contact)
        self.assertTrue(contact)
        
    def test_create(self):
        contact = MyContact(email="victor26@rochapps.com")
        contact.save()
        local_icontacts = iContact.objects.all()
        self.assertTrue(local_icontacts)
        
    def test_update(self):
        contact = MyContact(email="victor19@rochapps.com")
        contact.save()
        contact.firstName = 'victor'
        contact.save() #should call the update method on the observer model
        contact = self.observer.get_contact(contact)
        contact_firstName = contact['contact']['firstName']
        print contact_firstName
        self.assertEqual('victor', contact_firstName)
                
    def test_delete(self):
        contact = MyContact(email="victor21@rochapps.com")
        contact.save()
        time.sleep(10)
        icontact = self.observer.get_contact(contact)
        contactId = icontact['contact']['contactId']
        contact.delete()
        client = self.observer.client()
        contact = client.get_contact(contactId)
        print 'deleting contact'
        print contact
        self.assertRaises(IcontactException, client.get_contact, contactId)
