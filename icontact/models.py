from django.db import models
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

class iContactManager(models.Manager):
    """
    A custom manager for iContactContact model to get, create, update, and
    delete instances of the class.
    """
    
    def delete_contact_id(self, obj):
        """
        Deletes the record for the object.
        """
        ct = ContentType.objects.get_for_model(obj)
        try:
            contact = self.filter(
                content_type=ct, 
                object_id=obj.pk)
            contact.delete()
        except models.ObjectDoesNotExist:
            pass
    
    def get_contact_id(self, obj):
        """
        Gets iContactContact instance for a object, or returns None.
        """
        ct = ContentType.objects.get_for_model(obj)
        try:
            contact = self.get(
                content_type=ct, 
                object_id=obj.pk)
            contact_id = contact.contact_id
        except models.ObjectDoesNotExist:
            contact_id = None
        return contact_id
    
    def set_contact_id(self, obj, contact_id):
        """
        Sets the contactId on an object.
        """
        ct = ContentType.objects.get_for_model(obj)
        try:
            contact = self.get(
                content_type=ct, 
                object_id=obj.pk)
            contact.contact_id = contact_id
        except models.ObjectDoesNotExist:
            contact = iContact(
                content_type=ct, 
                object_id=obj.pk,
                contact_id=contact_id)
        contact.save()
        return contact
    

class iContact(models.Model):
    """
        iContactContact keep record of clientIds to be able to sync with the
        icontact API.
    """
    
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    object = generic.GenericForeignKey()
    #icontact contactId 
    contact_id = models.CharField(max_length=50)
    #manager to get, update, and delete instances
    objects = iContactManager()
    
    def __unicode__(self):
        return u"%s: %s" % (self.object, self.contact_id)
