import unittest

from django.test import TestCase
from django.conf import settings
from django.db import IntegrityError

from icontact.adapter import iContactData, iContactAdapter


class IcontactDataTests(TestCase):
    """
        tests for IcontactData class
    """
    
    def setUp(self):
        self.data = iContactData(email='info@rochapps.com')
            
    def test_get_data(self):
        data = self.data.get_data()
        self.assertEqual(14, len(data['contact']))
        self.assertEqual(data['contact']['email'],'info@rochapps.com')
        
    def test_default_status(self):
        self.data = iContactData(email='info@rochapps.com')
        self.assertEqual(self.data.status, 'normal')
        

class IcontactAdapterTests(TestCase):
    """
        Tests for IcontactAdapter class
    """
    
    def setUp(self):
        self.adapter = iContactAdapter()
        
    def test_get_contact_data(self):
        instance = 1
        self.assertRaises(NotImplementedError, self.adapter.get_contact_data,
            instance)
