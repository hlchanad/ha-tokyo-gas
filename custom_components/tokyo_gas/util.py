from .const import DOMAIN


def get_statistic_id(entry_id: str, identifier: str) -> str:
    # statistic_id has to be all lower case letters
    return f"{DOMAIN}:{entry_id.lower()}_{identifier}"
