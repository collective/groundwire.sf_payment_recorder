from decimal import Decimal
try:
    import json
except ImportError:
    import simplejson as json

import logging
import traceback
logger = logging.getLogger('groundwire.sf_payment_recorder')

from suds import WebFault

from zope.event import notify
from zope.annotation.interfaces import IAnnotations
from zope.app.component.hooks import getSite
from getpaid.core.interfaces import workflow_states
from getpaid.core.interfaces import ILineContainerTotals
from Products.CMFCore.utils import getToolByName

from groundwire.sf_payment_recorder.config import get_settings
from groundwire.sf_payment_recorder.interfaces import \
    ISalesforceUpdatingLineItem, ICustomFieldUpdatingLineItem, ISalesforceUpdatingPaymentInfo
from groundwire.sf_payment_recorder.utils import split_name, json_handler
from groundwire.sf_payment_recorder.events import OrderRecordedEvent
from collective.salesforce.credentials.utils import get_salesforce_suds_client


def record_order(order):
    settings = get_settings()
    client = get_salesforce_suds_client('GWOnlinePayment')

    # prepare enumerations
    NS = '{http://soap.sforce.com/schemas/class/OnlinePayment}'
    processor = client.factory.create(NS + 'Processor')
    paymentStatus = client.factory.create(NS + 'PaymentStatus')
    paymentType = client.factory.create(NS + 'PaymentType')
    recurringPeriod = client.factory.create(NS + 'RecurringPeriod')

    # contact info
    pmt = client.factory.create('PaymentInfo')
    contact = order.contact_information
    if hasattr(contact, 'sf_id'):
        pmt.contactId = contact.sf_id
    if hasattr(contact, 'first_name') and hasattr(contact, 'last_name'):
        pmt.firstName = contact.first_name
        pmt.lastName = contact.last_name
    else:
        pmt.firstName, pmt.lastName = split_name(order.contact_information.name)
    pmt.email = order.contact_information.email
    pmt.phone = order.contact_information.phone_number

    # billing info
    pmt.street = order.billing_address.bill_first_line
    if order.billing_address.bill_second_line:
        pmt.street += "\n" + order.billing_address.bill_second_line
    pmt.city = order.billing_address.bill_city
    pmt.state = order.billing_address.bill_state
    pmt.zip = order.billing_address.bill_postal_code
    pmt.country = order.billing_address.bill_country
    if (not settings.set_us_country) and (pmt.country == u'United States'):
        pmt.country = None

    # payment info
    pmt.pmtType = paymentType.CREDITCARD
    pmt.pmtProcessor = processor.AUTHNET
    pmt.txnId = order.user_payment_info_trans_id
    annotations = IAnnotations(order)
    pmt.last4digits = annotations.get('getpaid.authorizedotnet.cc_last_four', '')
    full_response = annotations.get('getpaid.authorizedotnet.full_response', '')
    # strip byte order mark if it's there
    pmt.paymentResponse = full_response.strip('\xef\xbb\xbf')

    # status
    if order.finance_state == workflow_states.order.finance.CHARGED:
        pmt.pmtStatus = paymentStatus.COMPLETED
    elif order.finance_state == workflow_states.order.finance.PAYMENT_DECLINED:
        pmt.pmtStatus = paymentStatus.DECLINED
    else:
        pmt.pmtStatus = paymentStatus.FAILED

    # line items
    items = []
    if hasattr(order.shopping_cart, 'getpaid_formgen_data'):
        order_custom_fields = order.shopping_cart.getpaid_formgen_data
    else:
        order_custom_fields = {}
    for cart_item in order.shopping_cart.values():
        item = client.factory.create('Item')
        item.name = cart_item.name
        item.code = cart_item.product_code
        item.amount = Decimal(str(cart_item.cost))
        item.quantity = cart_item.quantity
        if ISalesforceUpdatingLineItem.providedBy(cart_item):
            cart_item.update_salesforce_line_item(item, client)
        if ICustomFieldUpdatingLineItem.providedBy(cart_item):
            cart_item.update_order_custom_fields(order_custom_fields, client)
        if ISalesforceUpdatingPaymentInfo.providedBy(cart_item):
            cart_item.update_salesforce_payment_info(cart_item, pmt, client)
        items.append(item)
    pmt.itemList = items

    # custom fields
    if order_custom_fields:
        pmt.custom = json.dumps(order_custom_fields, default=json_handler)

    # total price
    cart_totals = ILineContainerTotals(order.shopping_cart)
    pmt.totalAmount = Decimal(str(cart_totals.getTotalPrice()))
    pmt.shipping = Decimal(str(cart_totals.getShippingCost()))
    pmt.tax = Decimal(str(cart_totals.getTaxCost()[0]['value']))

    # remove optional enumerated properties that cause problems
    # (this can go away once suds is fixed to not preset attributes
    #  that have minOccurs=0)
    if hasattr(pmt, 'payerMatchResult'):
        del pmt.payerMatchResult
    if hasattr(pmt, 'pmtPeriod'):
        del pmt.pmtPeriod

    # process recurring payments differently
    if order.shopping_cart.is_recurring():
        del pmt.txnId
        pmt.recurringTxnId = order.user_payment_info_trans_id
        cart_items = order.shopping_cart.values()
        assert len(cart_items) == 1
        recurring_item = cart_items[0]
        occurrences = recurring_item.total_occurrences
        if occurrences != 9999: # 9999 = recurring indefinitely
            pmt.occurrences = occurrences
        pmt.frequency = recurring_item.interval
        if recurring_item.unit == 'months':
            pmt.pmtPeriod = recurringPeriod.MONTH
        elif recurring_item.unit == 'days':
            pmt.pmtPeriod = recurringPeriod.DAY
        method = client.service.startRecurringPayments
    else:
        method = client.service.processSinglePayment

    logging.getLogger('suds.transport').setLevel(logging.DEBUG)

    # call the service
    try:
        res = method(pmt)
        if not res.success:
            raise Exception(res.errorMessage)
    except (WebFault, Exception):
        # catch exception and log (user doesn't need to know)
        logger.exception('Error recording order #%s to Salesforce.' % order.order_id)

        # e-mail admin
        if settings.email_recipient:
            site = getSite()
            MailHost = getToolByName(site, 'MailHost')
            message = "%s\n\n%s" % (traceback.format_exc(), str(pmt))
            subject = '%s: Error recording order #%s' % (site.absolute_url(), order.order_id)
            try:
                MailHost.secureSend(message, settings.email_recipient, 'plone@groundwire.org',
                                    subject=subject, subtype='plain', charset='utf-8')
            except:
                pass
    else:
        # log success
        try:
            logger.info('Recorded payment to Salesforce. Match result: %s.\n%s' % (pmt.payerMatchResult, pmt))
        except AttributeError:
            logger.info('Recorded payment to Salesforce. Could not get transaction data though.')

        # Fire the OrderRecorded event, with the response
        # and cart attached
        event = OrderRecordedEvent(order)
        event.sf_response = res
        notify(event)

    logging.getLogger('suds.transport').setLevel(logging.INFO)
