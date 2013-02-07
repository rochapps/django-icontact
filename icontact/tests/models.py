import unittest

from django.test import TestCase
from django.conf import settings
from django.db import IntegrityError
from django.db import models
from django.test.utils import override_settings
from django.core.management import call_command
from django.db.models import loading
from django.contrib.contenttypes.models import ContentType

from icontact.models import IContact

class MyContact(models.Model):
    email = models.EmailField()
    first_name = models.CharField(max_length=20)
    

class IContactManagerTests(TestCase):
    """
        iContact Custom Manager Tests
    """
    def setUp(self):
        settings.INSTALLED_APPS += ('icontact.tests',)
        loading.cache.loaded = False
        call_command('syncdb', verbosity=0)
        self.contact = MyContact(email="victor@rochapps.com")
        self.contact.save()
        
#        icontact = iContact(object=self.contact, contact_id=1)

    def tearDown(self):
        IContact.objects.all().delete()
        
    def test_delete_contact_id(self):
        icontact = IContact.objects.set_contact_id(
            obj=self.contact, 
            contact_id=1)
        IContact.objects.delete_contact_id(self.contact)    
        IContacts = IContact.objects.all()
        self.assertEqual(IContacts.count(), 0)
        #deleting an unexistant object should not raise any exception
        IContact.objects.delete_contact_id(self.contact)    
        iContacts = IContact.objects.all()
        self.assertEqual(IContacts.count(), 0)
        
    def test_delete_contact_id(self):
        contact_type = ContentType.objects.get_for_model(self.contact)
        icontact = IContact.objects.set_contact_id(
            obj=self.contact, 
            contact_id='101')
        contact_id = IContact.objects.get_contact_id(self.contact)    
        self.assertEqual(contact_id, icontact.contact_id)
        
    def test_set_contact_id(self):
        #it creates a contact a new instance if none matches the query
        icontact = IContact.objects.set_contact_id(
            obj=self.contact, 
            contact_id=1)
        IContacts = IContact.objects.all()
        self.assertEqual(IContacts.count(), 1)
        #if the object already exists it should just updated it
        icontact = IContact.objects.set_contact_id(
            obj=self.contact, 
            contact_id=2)
        icontacts = IContact.objects.all()
        self.assertEqual(icontacts.count(), 1)


class IContactModelTests(TestCase):
    """
        Tests for the iCotactContact model
    """
    def setUp(self):
        settings.INSTALLED_APPS += ('icontact.tests',)
        loading.cache.loaded = False
        call_command('syncdb', verbosity=0)
        self.contact = MyContact(email="victor@rochapps.com")
        self.contact.save()
        self.icontact = IContact.objects.set_contact_id(
            obj=self.contact, 
            contact_id=1)
            
    def test_unicode(self):
        representation = "%s: %s"%(self.contact, 1)
        self.assertEqual(representation, self.icontact.__unicode__())
