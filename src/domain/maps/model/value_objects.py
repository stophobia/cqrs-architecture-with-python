from __future__ import annotations

from enum import Enum

from domain.base.value_object import ValueObject


class StatesEnum(str, Enum):
    RS = 'Rio Grande do Sul'
    SP = 'São Paulo'
    SC = 'Santa Catarina'

    @classmethod
    def has_value(cls, value: str) -> bool:
        """Return True if the provided value matches any enum value."""
        return value in (member.value for member in cls)


class Address(ValueObject):
    """Value object representing a postal address."""

    house_number: str | int | None
    road: str
    sub_district: str
    district: str
    state: StatesEnum
    postcode: str
    country: str

    def is_valid_state(self) -> bool:
        """Check if the state belongs to the known StatesEnum."""
        return StatesEnum.has_value(self.state)
