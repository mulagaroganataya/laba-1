class DomainError(Exception):
    """Базовая ошибка предметной области."""


class ValidationError(DomainError):
    """Неверные данные/состояние."""


class NotFoundError(DomainError):
    """Сущность не найдена."""


class SeatUnavailableError(DomainError):
    """Место недоступно (уже занято)."""


class BookingStateError(DomainError):
    """Неверный переход состояния бронирования."""
