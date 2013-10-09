from zope.component import queryUtility
from plone.registry.interfaces import IRegistry
from groundwire.sf_payment_recorder.interfaces import ISalesforcePaymentRecorderSettings

SOCKET_TIMEOUT = 15 # seconds

def get_settings():
    registry = queryUtility(IRegistry, None)
    if registry is None:
        return
    
    return registry.forInterface(ISalesforcePaymentRecorderSettings, False)
