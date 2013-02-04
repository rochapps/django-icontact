""""
    Icontact Adapter
"""
class iContactData(object):
    """
        Takes all the possible field for creating
        an icontact contact:
        
        prefix:	string	Indicates the contact's salutation.	Miss
        firstName:	string	Indicates the contact's first name.	Mary
        lastName:	string	Indicates the contact's last name.	Smith
        suffix:	string	Indicates the contact's name qualifications.	III
        street:	string	Indicates the contact's address information.	2635 Meridian Parkway
        street2:	string	Indicates the contact's address information.	Suite 100
        city:	string	Indicates the contact's address information.	Durham
        state:	string	Indicates the contact's address information. No longer than 10 characters.	NC
        postalCode:	string	Indicates the contact's address information.	27713
        phone:	string	Indicates the contact's phone number.	8668039462
        fax	string:	Indicates the contact's fax number.	8668039462
        business:	string	Indicates the contact's business phone number.	8668039462
        status:	string (see note)	Indicates the subscription status of the contact. Proper values include normal and donotcontact.	pending
        
        required arguments:
        email: This field is required and it has to be a valid email address
    """
        

    def __init__(self, email, prefix="", firstName="", lastName="", suffix="",
            street="", street2="", city="", state="", postalCode="", phone="",
            fax="", business="", status="normal", contactId=None):
        """
            Instantiate an instance of the class.
            
            required fields: email
            
            Default values:
            status: "normal"   
        """ 
        
        self.email = email
        self.prefix	= prefix #contact's salutation.	Miss
        self.firstName = firstName
        self.lastName = lastName
        self.suffix	= suffix #contact's name qualifications.	III
        self.street	= street 
        self.street2 = street2 
        self.city = city   
        self.state = state   #No longer than 10 characters.	NC
        self.postalCode	= postalCode 
        self.phone = phone  #contact's phone number.	8668039462
        self.fax = fax	    #contact's fax number.	8668039462
        self.business = business #contact's business phone number.
        self.status	= status    #values normal and donotcontact, pending
        
    def get_data(self):
        """
            return a json seriazible object of all the attributes of the class
        """
        instance_data = self.__dict__
        icontact_data = {"contact": instance_data}
        return icontact_data
        

class iContactAdapter(object):
    """
        Adaptor classs.
    """
    def __init__(self):
        pass
        
    def get_contact_data(self, instance):
        """
            This method should be implemented by the user and should return an
            instance of IcontactData.
        """
        raise NotImplementedError
        
    
