from collections.abc import Callable  # recomendado nas docs
from typing import LiteralString, TypeAlias
from uuid import uuid4

IDGenerator: TypeAlias = Callable[[], str]


def make_id_generator(prefix: LiteralString) -> IDGenerator:
    """
    Returns a closure that generates unique IDs using the given *literal* prefix.
    Example output: "<prefix>_<32-hex>"
    """

    def _gen() -> str:
        return f"{prefix}_{uuid4().hex}"

    return _gen
