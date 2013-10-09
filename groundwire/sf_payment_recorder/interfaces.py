from zope.interface import Interface
from zope.component.interfaces import IObjectEvent
from zope import schema
from groundwire.sf_payment_recorder import _

class ISalesforcePaymentRecorderSettings(Interface):
    
    email_recipient = schema.ASCIILine(
        title = _(u'Recipient of failure e-mails'),
        description = _(u'If an order cannot be recorded, an e-mail will be sent here.'),
        required = False,
        )
    
    set_us_country = schema.Bool(
        title = _(u'Save country when it is United States'),
        default = False,
        )


class ISalesforceUpdatingLineItem(Interface):
    """Provides a method for getpaid line items to update the item recorded
    to Salesforce.
    """

    def update_salesforce_line_item(item, suds_client):
        """
        A hook for getpaid line items to modify the line item recorded to
        Salesforce.
        
        item = Salesforce line item under construction
        suds_client = suds client being used to talk to Salesforce
        """
        
class ISalesforceUpdatingPaymentInfo(Interface):
    """Provides a method for getpaid line items to update the Payment Info object recorded
    to Salesforce.
    """

    def update_salesforce_payment_info(item, pmt, suds_client):
        """
        A hook for getpaid line items to modify the payment info object recorded to
        Salesforce.
        
        item = Salesforce line item under construction
        pmt = OnlinePayments webservice PaymentInfo object
        suds_client = suds client being used to talk to Salesforce
        """
        
class ICustomFieldUpdatingLineItem(Interface):
    """Provides a method for getpaid line items to update the custom fields
    that get sent to Salesforce.
    """

    def update_order_custom_fields(custom_fields, suds_client):
        """
        A hook for getpaid line items to modify the custom fields for the
        order that gets recorded to Salesforce.

        custom fields = dictionary of field-value pairs (will be converted to
                                                         JSON elsewhere)
        suds_client = suds client being used to talk to Salesforce.
        
        See this package's README for more details on what you can do with the
        custom fields.
        """
        

class IOrderRecordedEvent(IObjectEvent):
    """ Event that fires when an order has been successfully recorded.
        Includes the order and response from salesforce.
    """
