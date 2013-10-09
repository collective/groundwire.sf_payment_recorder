import re
from datetime import date

INITIAL_RE = re.compile(r'^[a-zA-Z]\.?$')

def split_name(name):
    """Try to split a full name into first and last names.
    
    Currently it splits on spaces and counts the last word as the last name,
    unless the penultimate word starts with a lowercase letter (e.g. 'van Dyk'),
    in which case the penultimate word is included in the last name.

    If the last word in the first name is a single initial, it is dropped
    to facilitate de-duplication based on first name.
    
    We'll see if this is good enough.
    """
    parts = [part for part in name.strip().split(' ') if part]
    if len(parts) <= 1:
        return '', name
    try:
        if parts[-2][0].islower():
            # handle last names like van Dyk
            first, last = parts[:-2], parts[-2:]
        else:
            first, last = parts[:-1], [parts[-1]]

        # strip middle initials
        if len(first) > 1 and INITIAL_RE.match(first[-1]):
            first = first[:-1]

        return ' '.join(first), ' '.join(last)
    except IndexError:
        return '', ''

def json_handler(obj):
    """
    Default item handler for serializing dates to JSON.
    """
    
    if isinstance(obj, date):
        return obj.strftime('%Y-%m-%d')
    raise TypeError, 'Object of type %s with value of %s is not JSON serializable'
