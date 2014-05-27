from zope.component import adapter
from getpaid.core.interfaces import workflow_states
from getpaid.core.interfaces import IOrder
from groundwire.sf_payment_recorder.config import get_settings
from groundwire.sf_payment_recorder.record import record_order

try:
    from getpaid.hurry.workflow.interfaces import IWorkflowTransitionEvent
except ImportError:
    # BBB for hurry.workflow (pre-namespance change)
    from hurry.workflow.interfaces import IWorkflowTransitionEvent


canceled_states = (workflow_states.order.finance.PAYMENT_DECLINED,
                   workflow_states.order.finance.CANCELLED,
                   workflow_states.order.finance.CANCELLED_BY_PROCESSOR,)

@adapter(IOrder, IWorkflowTransitionEvent)
def handle_getpaid_workflow_transition(order, event):
    if order.finance_state != event.destination:
        return

    settings = get_settings()
    if settings is None:
        # groundwire.sf_payment_recorder not installed in this site
        return

    if order.finance_state == workflow_states.order.finance.CHARGED:
        record_order(order)
    elif order.finance_state in canceled_states:
        record_order(order)
