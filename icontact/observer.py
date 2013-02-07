"""
Observer for iContact instances

"""
import logging

from django.db.models import signals

from icontact.models import IContact
from icontact.client import IContactClient, IContactException

logger = logging.getLogger(__name__)

class IContactObserver(object):
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
            self._client = IContactClient()
        return self._client
        
    def get_contact(self, instance):
        """
            gets a contact from icontact service
        """
        contact_id = IContact.objects.get_contact_id(instance)
        logging.debug("contact id: {id}".format(id=contact_id))
        try:
            contact = self._client.get_contact(contact_id)
        except IContactException:
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
        logging.debug('Adapter: {adapter}'.format(adapter=adapter))
        client = self.client()
        contact = adapter.get_contact_data(instance) #IcontactData instance
        data = contact.get_data()
        logging.debug("contact's data: %s"%data)
        try:
            icontact = client.create_contact(payload=data)
            contact_id = icontact['contacts'][0]['contactId']
            subscription = client.subscribe(contact_id)
        except IContactException:
            return None
        IContact.objects.set_contact_id(instance, contact_id)   
    
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
            contact_id = icontact['contact']['contactId']
            client.update_contact(contact_id=contact_id, payload=data['contact'])
        except IContactException:
            return None
        IContact.objects.set_contact_id(instance, contact_id)
    
    def delete(self, sender, instance):
        """
        Deletes iContact record from their service and from our database
        """
        adapter = self.adapters[sender]
        client = self.client()
        contact = adapter.get_contact_data(instance) #IcontactData instance
        icontact = self.get_contact(instance)
        if not icontact: return None
        contact_id = icontact['contact']['contactId']
        try:
            client.delete_contact(contact_id) #delete from icontact
        except IContactException:
            pass
        IContact.objects.delete_contact_id(instance) #delete from database
