from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid


class ValidationError(Exception):
    pass


class BookingStateError(Exception):
    pass


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex}"


def ensure_nonempty(value: str, field_name: str) -> None:
    if not value or not value.strip():
        raise ValidationError(f"Поле '{field_name}' не должно быть пустым.")


class BookingStatus(str, Enum):
    DRAFT = "DRAFT"
    CONFIRMED = "CONFIRMED"
    CANCELED = "CANCELED"


@dataclass(slots=True)
class Customer:
    id: str
    name: str
    email: str

    def validate(self) -> None:
        ensure_nonempty(self.name, "name")
        if "@" not in self.email:
            raise ValidationError("Email должен содержать '@'.")


@dataclass(slots=True)
class Event:
    id: str
    title: str
    date: datetime

    def validate(self) -> None:
        ensure_nonempty(self.title, "title")


@dataclass(slots=True)
class Seat:
    id: str
    event_id: str
    row: int
    number: int
    price: int

    def validate(self) -> None:
        if self.row <= 0 or self.number <= 0:
            raise ValidationError("row и number должны быть > 0.")
        if self.price < 0:
            raise ValidationError("price не может быть отрицательной.")


@dataclass(slots=True)
class Booking:
    id: str
    customer_id: str
    event_id: str
    seat_id: str
    status: BookingStatus = BookingStatus.DRAFT
    created_at: datetime = field(default_factory=datetime.utcnow)

    def confirm(self) -> None:
        if self.status != BookingStatus.DRAFT:
            raise BookingStateError("Подтвердить можно только бронирование в статусе DRAFT.")
        self.status = BookingStatus.CONFIRMED

    def cancel(self) -> None:
        self.status = BookingStatus.CANCELED


def main() -> None:
    customer = Customer(id=new_id("cust"), name="Иван Иванов", email="ivan@mail.ru")
    customer.validate()

    event = Event(id=new_id("evt"), title="Концерт группы Python", date=datetime(2026, 3, 10, 19, 0))
    event.validate()

    seat = Seat(id=new_id("seat"), event_id=event.id, row=1, number=1, price=2000)
    seat.validate()

    booking = Booking(id=new_id("book"), customer_id=customer.id, event_id=event.id, seat_id=seat.id)
    print("Создано бронирование:", booking)

    booking.confirm()
    print("Подтверждено:", booking)


if __name__ == "__main__":
    try:
        main()
    except (ValidationError, BookingStateError) as e:
        print("Ошибка:", e)
