"""
Observer for iContact instances

"""
import logging

from django.db.models import signals

from icontact.models import iContact
from icontact.client import IcontactClient, IcontactException

logging.basicConfig(level=logging.DEBUG)

class iContactObserver(object):
    """
        Class that utilizes icontact client to sync model with icontact service
    """
    
    def __init__(self, client=None):
        """
        Initialize an instance of the CalendarObserver class.
        """
        self.adapters = {}
        self._client = client
    
    def observe(self, model, adapter):
        """
        Establishes a connection between the model and Google Calendar, using
        adapter to transform data.
        """
        self.adapters[model] = adapter
        signals.post_save.connect(self.on_update, sender=model)
        signals.post_delete.connect(self.on_delete, sender=model)
    
    def on_update(self, **kwargs):
        """
        Called by Django's signal mechanism when an observed model is updated.
        """
        created = kwargs.get('created', False)
        if created:
            logging.debug("Created")
            self.create(kwargs['sender'], kwargs['instance'])
            return 
        logging.debug("Updating")
        self.update(kwargs['sender'], kwargs['instance'])
    
    def on_delete(self, **kwargs):
        """
        Called by Django's signal mechanism when an observed model is deleted.
        """
        self.delete(kwargs['sender'], kwargs['instance'])
    
    def client(self):
        """
        Instantiate the client class to make authenticated calls to icontact.
        """
        if self._client is None:
            self._client = IcontactClient()
        return self._client
        
    def get_contact(self, instance):
        """
            gets a contact from icontact service
        """
        contact_id = iContact.objects.get_contact_id(instance)
        logging.debug("contact id: %s"%contact_id)
        try:
            contact = self._client.get_contact(contact_id)
        except IcontactException:
            return None
        logging.debug('contact retrived')
        logging.debug(contact)
        return contact

    def create(self, sender, instance):
        """
            creates a new contact on icontact's datata base as well as a
            iContact instance
        """
        adapter = self.adapters[sender]
        logging.debug('Adapter: %s'%adapter)
        client = self.client()
        contact = adapter.get_contact_data(instance) #IcontactData instance
        data = contact.get_data()
        logging.debug("contact's data: %s"%data)
        try:
            icontact = client.create_contact(payload=data)
            contactId = icontact['contacts'][0]['contactId']
            subscription = client.subscribe(contactId)
        except IcontactException:
            return
        iContact.objects.set_contact_id(instance, contactId)   
    
    def update(self, sender, instance):
        """
        Update or create an Icontact Contact.
        
        By default the client subscribes to the deault list specified in 
        settings.py
        """
        adapter = self.adapters[sender]
        client = self.client()
        contact = adapter.get_contact_data(instance) #IcontactData instance
        data = contact.get_data()
        logging.debug(data)
        logging.debug(data['contact'])
        try: 
            icontact = self.get_contact(instance)
            contactId = icontact['contact']['contactId']
            client.update_contact(contactId=contactId, payload=data['contact'])
        except IcontactException:
            return None
        iContact.objects.set_contact_id(instance, contactId)
    
    def delete(self, sender, instance):
        """
        Deletes iContact record from their service and from our database
        """
        adapter = self.adapters[sender]
        client = self.client()
        contact = adapter.get_contact_data(instance) #IcontactData instance
        icontact = self.get_contact(instance)
        if not icontact: return None
        contactId = icontact['contact']['contactId']
        try:
            client.delete_contact(contactId) #delete from icontact
        except IcontactException:
            pass
        iContact.objects.delete_contact_id(instance) #delete from database
