Introduction
============

``groundwire.sf_payment_recorder`` records GetPaid orders in Salesforce
using the ``GWOnlinePayment`` webservice.

When adding custom fields to line items using the update_order_custom_fields 
hook, note the following documentation, which appears on the Apex for
processing the webservice::

    updateSObjectFromJSON method
    looks for field values in a json string and sets them in an sobject
    
    JSON in the 'custom' property can take one of two forms:
    you can specify generic field name/value pairs for any object, or set
    fields on a specific object by setting a value for the object name (e.g.
    contact, account) and then nesting JSON with field values 
    FORM 1:
        {"leadsource": "Secret", "my_custom_field__c": "Sauce"}
    FORM 2: 
        {"contact": {"leadsource": "Secret", "my_custom_field__c": "Sauce"}, 
         "account": {"description": "Special" },
         "opportunity": {"leadsource": "Secret", "my_custom_field__c": "Sauce"}, 
         "GWBase__oppPayment__c": {"my_custom_field__c": "something"} }
    
    The '__c' suffix on custom fields is optional in the JSON - it will try to
    find fields with or without

(Also note that if just a string is passed through, it is assumed to be a
campaign id. This is primarily to support PayPal use cases; it's probably
preferable to be more explicit in Python code.)