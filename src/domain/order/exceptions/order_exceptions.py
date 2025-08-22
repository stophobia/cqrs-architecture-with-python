from __future__ import annotations

from fastapi import status

from exceptions import OrderingServiceException


class OrderAlreadyCancelledException(OrderingServiceException):
    """Raised when trying to transition or act on an already-cancelled order."""

    status_code = status.HTTP_409_CONFLICT
    name = 'ORDER_ALREADY_CANCELLED'
    message = 'order is already cancelled'


class OrderAlreadyPaidException(OrderingServiceException):
    """Raised when trying to transition or act on an already-paid order."""

    status_code = status.HTTP_409_CONFLICT
    name = 'ORDER_ALREADY_PAID'
    message = 'order is already paid'


class PaymentNotVerifiedException(OrderingServiceException):
    """Raised when a payment verification precondition fails."""

    status_code = status.HTTP_403_FORBIDDEN
    name = 'PAYMENT_NOT_VERIFIED'
    message = 'payment not verified'


class EntityNotFound(OrderingServiceException):
    """Raised when an entity cannot be located."""

    status_code = status.HTTP_404_NOT_FOUND
    name = 'ENTITY_NOT_FOUND'
    message = 'entity not found'


class EntityOutdated(OrderingServiceException):
    """Raised when an incoming aggregate version is older than the current one."""

    status_code = status.HTTP_409_CONFLICT
    name = 'ENTITY_OUTDATED'
    message = 'entity version is outdated'


class PersistenceError(OrderingServiceException):
    """Raised for storage/DB related failures."""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    name = 'PERSISTENCE_ERROR'
    message = 'persistence error'


class OrderIdRequired(OrderingServiceException):
    """Raised when order_id is missing or blank."""

    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    name = 'ORDER_ID_REQUIRED'
    message = 'order_id is required'


class OrderIdInvalid(OrderingServiceException):
    """Raised when order_id has an invalid format."""

    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    name = 'ORDER_ID_INVALID'
    message = 'order_id must be a valid UUID'


class OrderStatusRequired(OrderingServiceException):
    """Raised when status is missing or blank."""

    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    name = 'ORDER_STATUS_REQUIRED'
    message = 'status is required'


class OrderStatusInvalid(OrderingServiceException):
    """Raised when status is not a recognized enum value."""

    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    name = 'ORDER_STATUS_INVALID'
    message = 'invalid status value'


class OrderNotFound(OrderingServiceException):
    """Raised when an order cannot be located."""

    status_code = status.HTTP_404_NOT_FOUND
    name = 'ORDER_NOT_FOUND'
    message = 'order not found'


class CannotUpdateToStatus(OrderingServiceException):
    """Raised when a requested status transition is not allowed."""

    status_code = status.HTTP_403_FORBIDDEN
    name = 'CANNOT_UPDATE_TO_STATUS'
    message = 'cannot update order status to the requested value'


class CannotPayCancelled(OrderingServiceException):
    """Raised when attempting to pay an already-cancelled order."""

    status_code = status.HTTP_409_CONFLICT
    name = 'CANNOT_PAY_CANCELLED'
    message = "cannot pay for order when it's already cancelled"


class CannotPayAlreadyPaid(OrderingServiceException):
    """Raised when attempting to pay an already-paid order."""

    status_code = status.HTTP_409_CONFLICT
    name = 'CANNOT_PAY_ALREADY_PAID'
    message = "cannot pay for order when it's already paid"


class PaymentVerificationFailed(OrderingServiceException):
    """Raised when payment verification fails during a transition."""

    status_code = status.HTTP_403_FORBIDDEN
    name = 'PAYMENT_VERIFICATION_FAILED'
    message = 'payment verification failed'


class CannotCancelAlreadyCancelled(OrderingServiceException):
    """Raised when attempting to cancel an already-cancelled order."""

    status_code = status.HTTP_409_CONFLICT
    name = 'CANNOT_CANCEL_ALREADY_CANCELLED'
    message = "cannot cancel order when it's already cancelled"


class CannotCancelAlreadyPaid(OrderingServiceException):
    """Raised when attempting to cancel a paid order."""

    status_code = status.HTTP_409_CONFLICT
    name = 'CANNOT_CANCEL_ALREADY_PAID'
    message = "cannot cancel order when it's already paid"
