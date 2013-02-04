"""
Icontact client for python
"""
import requests
import logging
import json

from django.conf import settings

logging.basicConfig(level=logging.DEBUG)

STATUS_CODES = {
    200: 'OK	Your request was processed successfully',
    400: 'Your data could not be parsed or your request contained invalid data',
    401: 'You are not logged in',
    402: 'Payment Required',
    403: 'You are logged in, but do not have permission to perform that action',
    404: 'Not Found	You have requested a resource that cannot be found',
    405: 'Method Not Allowed',
    406: 'Unsupported format Icontact returns data in XML or JSON only',
    415: 'Unsupported format. You can make requests in XML or JSON.',
    500: 'Internal Server Error',
    501: 'Not Implemented',
    503: 'Service Unavailable',
    507: 'Insufficient Space'
}


class IcontactException(Exception): pass
    
    
class IcontactClient(object):
    """
        Icontact Client to create, update, delete contacts, and subscribe
        them to a list.
        
        Class doesnt take any required arguments to be instantiated, however 
        the following settings need to be provide in your settings.py file.
        
        ICONTACT_API_KEY: The Key that was given to you when you registered
                        your application.
                        
        ICONTACT_USERNAME: The username you created to log into their sandbox.
        
        ICONTACT_PASSWORD: The password you assigned to your application, this
                        is different from your login password.
                        
        ICONTACT_API_VERSION: The api version you are using.
        
        ICONTACT_URL: This determines whether you are in production or sandbox
                    enviroment. The options are:
                    https://app.sandbox.icontact.com/icp/
                    https://app.icontact.com/icp/
                    
        ICONTACT_DEFAULT_LIST: Default list to subscribe users to.
        
        ICONTACT_ACCOUNT_ID: Account ID
        
        ICONTACT_FOLDER_ID: Folder id
        
    """    
        

    def __init__(self, api_key=settings.ICONTACT_API_KEY,
            username=settings.ICONTACT_USERNAME, 
            password=settings.ICONTACT_PASSWORD,
            account_id=settings.ICONTACT_ACCOUNT_ID,
            folder_id=settings.ICONTACT_FOLDER_ID):
        """
            Instantiate a instance of the class, not arguments are required.
        """
            
        self.api_key = api_key 
        self.username = username
        self.password = password
        self.api_version = settings.ICONTACT_API_VERSION
        self.account_id = account_id
        self.folder_id = folder_id
    
    def _get_headers(self, **kwargs):
        """
            Headers required to authenticate your request. 
            
            You can pass extra headers by passing them into the ***kwargs
        """
        headers = {
            'Accept':'application/json',
            'Content-Type':'application/json',
            'Api-Version':self.api_version,
            'Api-AppId':self.api_key,
            'Api-Username':self.username, 
            'API-Password':self.password 
            }
        headers.update(kwargs)
        return headers
        
    def prepare_url(self, resource_url=""):
        """
            Prepares an url to make requests to.
            
            It return an url in the form:
            https://app.sandbox.icontact.com/icp/a/app_id/c/folder_id/resource_path
        
        """
        url = "{base}a/{account_id}/c/{folder_id}/{resource_url}".format(
            base=settings.ICONTACT_URL, 
            account_id=self.account_id,
            folder_id=self.folder_id,
            resource_url=resource_url)
        logging.debug('request url: %s'%url)
        return url
        
    def process_response(self, response):
        """
            returns json object if the request was successful, otherwise
            raises an IcontactException.
        """
        status_code = response.status_code
        logging.debug('status code: %s'%status_code)
        logging.debug(response)
        if status_code == 200:
            data = response.json()
            logging.debug(data)
            if 'warnings' in data:
                raise IcontactException(' '.join(data['warnings']))
            if 'errors' in data:
                raise IcontactException(' '.join(data['errors']))
            return data
        message = STATUS_CODES.get(int(status_code), 404)
        logging.debug(message)
        raise IcontactException(message)
    
    def create_contact(self, payload=None):
        """
            Creates contact from dict. The data dictionary need to be in the
            format: {'contact':{"email":"info@rochapps.com"}} 
            
            payload is a python dict that must at least contain the key "email", 
            as the email field is required by Icontact.
        """
        logging.debug('method: POST')
        url = self.prepare_url(resource_url='contacts/')
        payload = payload or {}
        r = requests.post(url, data=json.dumps(payload), 
            headers=self._get_headers())
        contact = self.process_response(r)
        return contact

    def get_contact(self, contactId):
        """
            Gets a contact with the provided contactId, if it doesn't find a
            match it raises an IcontactException
        """
        logging.debug('method: GET')
        url = self.prepare_url(resource_url='contacts/{contactId}'.format(
            contactId=contactId))
        r = requests.get(url, headers=self._get_headers())
        json_response = self.process_response(r)
        return json_response

    def update_contact(self, contactId, payload=None):
        """
            Updates a contact with the provided contactId, if it doesn't find a
            match it raises an IcontactException
        """
        logging.debug('method: PUT')
        url = self.prepare_url(resource_url='contacts/{contactId}'.format(
            contactId=contactId))
        payload = payload or {}
        r = requests.put(url, data=json.dumps(payload), 
            headers=self._get_headers())
        json_response = self.process_response(r)
        return json_response
        
    def delete_contact(self, contactId):
        """
            Deletes a contact with the provided contactId, if it doesn't find a
            match it raises an IcontactException.
            
            Return an empty list if deleted succesfully.
        """
        logging.debug('method: DELETE')
        url = self.prepare_url(resource_url='contacts/{contactId}'.format(
            contactId=contactId))
        r = requests.delete(url, headers=self._get_headers())
        json_response = self.process_response(r)
        return json_response
        
                        
    def get_contacts(self):
        """
            Gets all contacts.
        """
        logging.debug('method: GET')
        url = self.prepare_url(resource_url='contacts/')
        r = requests.get(url, headers=self._get_headers())
        json_response = self.process_response(r)
        return json_response
        
    def subscribe(self, contactId, listId=settings.ICONTACT_DEFAULT_LIST):
        """
            Subscribe contact that matches the provided contactId to the
            default list.
            
            Optional args:
            
            listId: an Integer reprenting the id of the list you want the
                contact to be subscribed to.
        """
        logging.debug('method: POST')
        url = self.prepare_url(resource_url='subscriptions/')
        payload = {'subscription':{'contactId':contactId, 'listId':listId,
            'status':'normal'}}
        r = requests.post(url, data=json.dumps(payload), 
            headers=self._get_headers())
        json_response = self.process_response(r)
        return json_response
