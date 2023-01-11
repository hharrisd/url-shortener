import secrets
import string
from .models import Link


def create_random_key(length: int = 6) -> str:
    chars = string.ascii_lowercase + string.ascii_uppercase + string.digits
    return "".join(secrets.choice(chars) for _ in range(length))


def create_unique_random_key() -> str:
    key = create_random_key()
    while Link.objects.filter(key__iexact=key).exists():
        key = create_random_key()
    return key


def is_alias_available(alias: str) -> str | None:
    if Link.objects.filter(key__iexact=alias).exists():
        return None
    return alias
