from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional
import json
import uuid
import xml.etree.ElementTree as ET

from exceptions import (
    ValidationError,
    NotFoundError,
    SeatUnavailableError,
    BookingStateError,
)
from models import Customer, Event, Seat, Booking, BookingStatus, dt_to_str, str_to_dt


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex}"


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

    # ---- JSON ----

    def to_dict(self) -> dict:
        return {
            "customers": [c.to_dict() for c in self.customers.values()],
            "events": [e.to_dict() for e in self.events.values()],
            "seats": [s.to_dict() for s in self.seats.values()],
            "bookings": [b.to_dict() for b in self.bookings.values()],
        }

    @staticmethod
    def from_dict(d: dict) -> "Repository":
        repo = Repository()
        for c in d.get("customers", []):
            obj = Customer.from_dict(c)
            repo.customers[obj.id] = obj
        for e in d.get("events", []):
            obj = Event.from_dict(e)
            repo.events[obj.id] = obj
        for s in d.get("seats", []):
            obj = Seat.from_dict(s)
            repo.seats[obj.id] = obj
        for b in d.get("bookings", []):
            obj = Booking.from_dict(b)
            repo.bookings[obj.id] = obj
        return repo

    def save_json(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

    @staticmethod
    def load_json(path: str) -> "Repository":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return Repository.from_dict(data)

    # ---- XML ----

    def to_xml_element(self) -> ET.Element:
        root = ET.Element("TicketSystem")

        customers_el = ET.SubElement(root, "Customers")
        for c in self.customers.values():
            el = ET.SubElement(customers_el, "Customer", {"id": c.id})
            ET.SubElement(el, "Name").text = c.name
            ET.SubElement(el, "Email").text = c.email

        events_el = ET.SubElement(root, "Events")
        for e in self.events.values():
            el = ET.SubElement(events_el, "Event", {"id": e.id})
            ET.SubElement(el, "Title").text = e.title
            ET.SubElement(el, "Date").text = dt_to_str(e.date)

        seats_el = ET.SubElement(root, "Seats")
        for s in self.seats.values():
            el = ET.SubElement(seats_el, "Seat", {"id": s.id})
            ET.SubElement(el, "EventId").text = s.event_id
            ET.SubElement(el, "Row").text = str(s.row)
            ET.SubElement(el, "Number").text = str(s.number)
            ET.SubElement(el, "Price").text = str(s.price)

        bookings_el = ET.SubElement(root, "Bookings")
        for b in self.bookings.values():
            el = ET.SubElement(bookings_el, "Booking", {"id": b.id})
            ET.SubElement(el, "CustomerId").text = b.customer_id
            ET.SubElement(el, "EventId").text = b.event_id
            ET.SubElement(el, "SeatId").text = b.seat_id
            ET.SubElement(el, "Status").text = b.status.value
            ET.SubElement(el, "CreatedAt").text = dt_to_str(b.created_at)

        return root

    @staticmethod
    def from_xml_element(root: ET.Element) -> "Repository":
        repo = Repository()

        customers_el = root.find("Customers")
        if customers_el is not None:
            for el in customers_el.findall("Customer"):
                cid = el.get("id", "")
                name = el.findtext("Name") or ""
                email = el.findtext("Email") or ""
                c = Customer(id=cid, name=name, email=email)
                c.validate()
                repo.customers[c.id] = c

        events_el = root.find("Events")
        if events_el is not None:
            for el in events_el.findall("Event"):
                eid = el.get("id", "")
                title = el.findtext("Title") or ""
                date_s = el.findtext("Date") or ""
                e = Event(id=eid, title=title, date=str_to_dt(date_s))
                e.validate()
                repo.events[e.id] = e

        seats_el = root.find("Seats")
        if seats_el is not None:
            for el in seats_el.findall("Seat"):
                sid = el.get("id", "")
                event_id = el.findtext("EventId") or ""
                row = int(el.findtext("Row") or "0")
                number = int(el.findtext("Number") or "0")
                price = int(el.findtext("Price") or "0")
                s = Seat(id=sid, event_id=event_id, row=row, number=number, price=price)
                s.validate()
                repo.seats[s.id] = s

        bookings_el = root.find("Bookings")
        if bookings_el is not None:
            for el in bookings_el.findall("Booking"):
                bid = el.get("id", "")
                customer_id = el.findtext("CustomerId") or ""
                event_id = el.findtext("EventId") or ""
                seat_id = el.findtext("SeatId") or ""
                status = BookingStatus(el.findtext("Status") or "DRAFT")
                created_at = str_to_dt(el.findtext("CreatedAt") or dt_to_str(datetime.utcnow()))
                b = Booking(
                    id=bid,
                    customer_id=customer_id,
                    event_id=event_id,
                    seat_id=seat_id,
                    status=status,
                    created_at=created_at,
                )
                repo.bookings[b.id] = b

        return repo

    def save_xml(self, path: str) -> None:
        root = self.to_xml_element()
        tree = ET.ElementTree(root)
        ET.indent(tree, space="  ")
        tree.write(path, encoding="utf-8", xml_declaration=True)

    @staticmethod
    def load_xml(path: str) -> "Repository":
        tree = ET.parse(path)
        root = tree.getroot()
        if root.tag != "TicketSystem":
            raise ValidationError("Неверный корневой тег XML. Ожидался <TicketSystem>.")
        return Repository.from_xml_element(root)