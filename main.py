from dataclasses import dataclass
from datetime import datetime
import uuid


class ValidationError(Exception):
    pass


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex}"


def ensure_nonempty(value: str, field_name: str) -> None:
    if not value or not value.strip():
        raise ValidationError(f"Поле '{field_name}' не должно быть пустым.")


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


def main() -> None:
    customer = Customer(id=new_id("cust"), name="Иван Иванов", email="ivan@mail.ru")
    customer.validate()

    event = Event(id=new_id("evt"), title="Концерт группы Python", date=datetime(2026, 3, 10, 19, 0))
    event.validate()

    seat = Seat(id=new_id("seat"), event_id=event.id, row=1, number=1, price=2000)
    seat.validate()

    print("OK:", customer)
    print("OK:", event)
    print("OK:", seat)


if __name__ == "__main__":
    try:
        main()
    except ValidationError as e:
        print("Ошибка валидации:", e)
