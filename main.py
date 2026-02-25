from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict
import uuid


class ValidationError(Exception):
    pass


class NotFoundError(Exception):
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


@dataclass
class Repository:
    customers: Dict[str, Customer] = field(default_factory=dict)
    events: Dict[str, Event] = field(default_factory=dict)
    seats: Dict[str, Seat] = field(default_factory=dict)
    bookings: Dict[str, Booking] = field(default_factory=dict)

    def add_customer(self, name: str, email: str) -> Customer:
        c = Customer(id=new_id("cust"), name=name, email=email)
        c.validate()
        self.customers[c.id] = c
        return c

    def add_event(self, title: str, date: datetime) -> Event:
        e = Event(id=new_id("evt"), title=title, date=date)
        e.validate()
        self.events[e.id] = e
        return e

    def add_seat(self, event_id: str, row: int, number: int, price: int) -> Seat:
        if event_id not in self.events:
            raise NotFoundError(f"Событие не найдено: {event_id}")
        s = Seat(id=new_id("seat"), event_id=event_id, row=row, number=number, price=price)
        s.validate()
        self.seats[s.id] = s
        return s

    def create_booking(self, customer_id: str, event_id: str, seat_id: str) -> Booking:
        if customer_id not in self.customers:
            raise NotFoundError(f"Клиент не найден: {customer_id}")
        if event_id not in self.events:
            raise NotFoundError(f"Событие не найдено: {event_id}")
        if seat_id not in self.seats:
            raise NotFoundError(f"Место не найдено: {seat_id}")

        b = Booking(id=new_id("book"), customer_id=customer_id, event_id=event_id, seat_id=seat_id)
        self.bookings[b.id] = b
        return b


def main() -> None:
    repo = Repository()

    customer = repo.add_customer("Иван Иванов", "ivan@mail.ru")
    event = repo.add_event("Концерт группы Python", datetime(2026, 3, 10, 19, 0))
    seat1 = repo.add_seat(event.id, 1, 1, 2000)

    booking = repo.create_booking(customer.id, event.id, seat1.id)
    print("Создано бронирование:", booking)

    repo.bookings[booking.id].confirm()
    print("Подтверждено:", repo.bookings[booking.id])


if __name__ == "__main__":
    try:
        main()
    except (ValidationError, NotFoundError, BookingStateError) as e:
        print("Ошибка:", e)
