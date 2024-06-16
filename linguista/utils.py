#
#
#   Utils
#
#

from rich.console import Console


def debug(*message):
    console = Console()
    message_str = "[DEBUG] " + " ".join([str(m) for m in message])
    console.print(message_str, style="bold yellow")


def strtobool(val):
    """Convert a string representation of truth to true (1) or false (0).
    True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
    are 'n', 'no', 'f', 'false', 'off', and '0'.  Raises ValueError if
    'val' is anything else.
    """
    val = val.lower()
    if val in ('y', 'yes', 't', 'true', 'on', '1'):
        return 1
    elif val in ('n', 'no', 'f', 'false', 'off', '0'):
        return 0
    else:
        raise ValueError("invalid truth value %r" % (val,))


def extract_digits(input_string):
    return ''.join(filter(lambda x: x.isdigit() or x == '.', input_string))
