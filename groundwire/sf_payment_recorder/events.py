from zope.component.interfaces import ObjectEvent
from zope.interface import implements
from groundwire.sf_payment_recorder.interfaces import \
    IOrderRecordedEvent

class OrderRecordedEvent(ObjectEvent):
    """
    An object event that indicates that the cart has been recorded. Includes the order
    and response from the salesforce webservice.
    """
    sf_response = None
    
    implements(IOrderRecordedEvent)

