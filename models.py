from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from exceptions import ValidationError, BookingStateError
from utils import ensure_nonempty, dt_to_str, str_to_dt


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

    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name, "email": self.email}

    @staticmethod
    def from_dict(d: dict) -> "Customer":
        c = Customer(id=d["id"], name=d["name"], email=d["email"])
        c.validate()
        return c


@dataclass(slots=True)
class Event:
    id: str
    title: str
    date: datetime

    def validate(self) -> None:
        ensure_nonempty(self.title, "title")

    def to_dict(self) -> dict:
        return {"id": self.id, "title": self.title, "date": dt_to_str(self.date)}

    @staticmethod
    def from_dict(d: dict) -> "Event":
        e = Event(id=d["id"], title=d["title"], date=str_to_dt(d["date"]))
        e.validate()
        return e


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

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "event_id": self.event_id,
            "row": self.row,
            "number": self.number,
            "price": self.price,
        }

    @staticmethod
    def from_dict(d: dict) -> "Seat":
        s = Seat(
            id=d["id"],
            event_id=d["event_id"],
            row=int(d["row"]),
            number=int(d["number"]),
            price=int(d["price"]),
        )
        s.validate()
        return s


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

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "event_id": self.event_id,
            "seat_id": self.seat_id,
            "status": self.status.value,
            "created_at": dt_to_str(self.created_at),
        }

    @staticmethod
    def from_dict(d: dict) -> "Booking":
        return Booking(
            id=d["id"],
            customer_id=d["customer_id"],
            event_id=d["event_id"],
            seat_id=d["seat_id"],
            status=BookingStatus(d.get("status", "DRAFT")),
            created_at=str_to_dt(d["created_at"]),
        )