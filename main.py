from dataclasses import dataclass
from datetime import datetime
import uuid


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex}"


@dataclass(slots=True)
class Customer:
    id: str
    name: str
    email: str


@dataclass(slots=True)
class Event:
    id: str
    title: str
    date: datetime


def main() -> None:
    customer = Customer(id=new_id("cust"), name="Иван Иванов", email="ivan@mail.ru")
    event = Event(id=new_id("evt"), title="Концерт группы Python", date=datetime(2026, 3, 10, 19, 0))

    print("Создан клиент:", customer)
    print("Создано событие:", event)


if __name__ == "__main__":
    main()
