from __future__ import annotations

from typing import Any, TypeVar

from pydantic import BaseModel, ConfigDict, GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema

ImplementationType = TypeVar('ImplementationType', bound='ValueObject')


class ValueObject(BaseModel):
    """Base class for immutable value objects."""

    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True)

    def __eq__(self: ImplementationType, other: object) -> bool:
        if not isinstance(other, type(self)):
            return False
        return self.model_dump() == other.model_dump()


class StrIdValueObject(str):
    """Base class for string-based identifier value objects."""

    @classmethod
    def validate(cls, __input_value: Any, _: core_schema.ValidationInfo) -> StrIdValueObject:
        if not isinstance(__input_value, str):
            raise TypeError(f"expected str, got {type(__input_value).__name__}")
        if not __input_value.strip():
            raise ValueError('string identifier cannot be blank')
        return cls(__input_value)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.with_info_after_validator_function(
            cls.validate,
            handler(str),
            field_name=handler.field_name,
        )
