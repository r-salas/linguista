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
