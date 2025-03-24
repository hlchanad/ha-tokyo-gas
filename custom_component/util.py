"""Common module for simple util"""

from .const import DOMAIN


def get_statistic_id(entry_id: str, identifier: str) -> str:
    """Format the statistic id"""

    # statistic_id has to be all lower case letters
    return f"{DOMAIN}:{entry_id.lower()}_{identifier}"
