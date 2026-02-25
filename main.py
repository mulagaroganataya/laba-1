from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, Optional
import uuid


class DomainError(Exception):
    pass


class ValidationError(DomainError):
    pass


class NotFoundError(DomainError):
    pass


class SeatUnavailableError(DomainError):
    pass


class BookingStateError(DomainError):
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
        self.get_event(event_id)

        # уникальность (row, number) в рамках события
        for s in self.seats.values():
            if s.event_id == event_id and s.row == row and s.number == number:
                raise ValidationError("Такое место (row, number) уже существует для этого события.")

        seat = Seat(id=new_id("seat"), event_id=event_id, row=row, number=number, price=price)
        seat.validate()
        self.seats[seat.id] = seat
        return seat

    def is_seat_taken(self, seat_id: str, ignore_booking_id: Optional[str] = None) -> bool:
        for b in self.bookings.values():
            if ignore_booking_id and b.id == ignore_booking_id:
                continue
            if b.seat_id == seat_id and b.status == BookingStatus.CONFIRMED:
                return True
        return False

    def create_booking(self, customer_id: str, event_id: str, seat_id: str) -> Booking:
        self.get_customer(customer_id)
        self.get_event(event_id)
        seat = self.get_seat(seat_id)

        if seat.event_id != event_id:
            raise ValidationError("Выбранное место не относится к выбранному событию.")

        if self.is_seat_taken(seat_id):
            raise SeatUnavailableError("Место уже занято.")

        booking = Booking(id=new_id("book"), customer_id=customer_id, event_id=event_id, seat_id=seat_id)
        self.bookings[booking.id] = booking
        return booking

    def confirm_booking(self, booking_id: str) -> Booking:
        b = self.get_booking(booking_id)
        if b.status == BookingStatus.CANCELED:
            raise BookingStateError("Нельзя подтвердить отменённое бронирование.")
        if self.is_seat_taken(b.seat_id, ignore_booking_id=b.id):
            raise SeatUnavailableError("Место уже занято другим бронированием.")
        b.confirm()
        return b

    def cancel_booking(self, booking_id: str) -> Booking:
        b = self.get_booking(booking_id)
        b.cancel()
        return b

    def get_customer(self, customer_id: str) -> Customer:
        try:
            return self.customers[customer_id]
        except KeyError as e:
            raise NotFoundError(f"Клиент не найден: {customer_id}") from e

    def get_event(self, event_id: str) -> Event:
        try:
            return self.events[event_id]
        except KeyError as e:
            raise NotFoundError(f"Событие не найдено: {event_id}") from e

    def get_seat(self, seat_id: str) -> Seat:
        try:
            return self.seats[seat_id]
        except KeyError as e:
            raise NotFoundError(f"Место не найдено: {seat_id}") from e

    def get_booking(self, booking_id: str) -> Booking:
        try:
            return self.bookings[booking_id]
        except KeyError as e:
            raise NotFoundError(f"Бронирование не найдено: {booking_id}") from e


def main() -> None:
    repo = Repository()

    customer = repo.add_customer("Иван Иванов", "ivan@mail.ru")
    event = repo.add_event("Концерт группы Python", datetime(2026, 3, 10, 19, 0))
    seat1 = repo.add_seat(event.id, 1, 1, 2000)

    booking = repo.create_booking(customer.id, event.id, seat1.id)
    print("Создано бронирование:", booking)

    repo.confirm_booking(booking.id)
    print("Подтверждено:", repo.get_booking(booking.id))

    print("\nПробуем занять то же место вторым бронированием:")
    try:
        repo.create_booking(customer.id, event.id, seat1.id)
    except SeatUnavailableError as e:
        print("Ожидаемая ошибка:", e)


if __name__ == "__main__":
    try:
        main()
    except DomainError as e:
        print("Ошибка домена:", e)
    except Exception as e:
        print(f"Непредвиденная ошибка: {type(e).__name__}: {e}")
