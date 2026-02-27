from datetime import datetime
import json
import xml.etree.ElementTree as ET

from exceptions import DomainError, SeatUnavailableError
from repository import Repository


def main() -> None:
    print("Демонстрация работы системы бронирования\n")

    repo = Repository()

    customer = repo.add_customer("Иван Иванов", "ivan@mail.ru")
    print("Создан клиент:", customer)

    event = repo.add_event("Концерт группы Python", datetime(2026, 3, 10, 19, 0))
    print("Создано событие:", event)

    seat1 = repo.add_seat(event.id, 1, 1, 2000)
    seat2 = repo.add_seat(event.id, 1, 2, 2000)
    print("Созданы места:", seat1, seat2)

    booking = repo.create_booking(customer.id, event.id, seat1.id)
    print("Создано бронирование (DRAFT):", booking)

    repo.confirm_booking(booking.id)
    print("Бронирование подтверждено:", repo.get_booking(booking.id))

    print("\nПробуем занять уже занятое место:")
    try:
        repo.create_booking(customer.id, event.id, seat1.id)
    except SeatUnavailableError as e:
        print("Ожидаемая ошибка:", e)

    repo.save_json("demo.json")
    print("\nСохранено в demo.json")

    repo_from_json = Repository.load_json("demo.json")
    print("Загружено из demo.json")
    print("Events after load:", repo_from_json.events)

    repo.save_xml("demo.xml")
    print("\nСохранено в demo.xml")

    repo_from_xml = Repository.load_xml("demo.xml")
    print("Загружено из demo.xml")
    print("Bookings after load:", repo_from_xml.bookings)

    print("\nДемонстрация завершена успешно.")


if __name__ == "__main__":
    try:
        main()
    except DomainError as e:
        print("Ошибка домена:", e)
    except ValueError:
        print("Ошибка: неверный формат числа/даты.")
    except FileNotFoundError:
        print("Ошибка: файл не найден.")
    except PermissionError:
        print("Ошибка: нет прав доступа к файлу.")
    except json.JSONDecodeError:
        print("Ошибка: файл JSON повреждён или имеет неверный формат.")
    except ET.ParseError:
        print("Ошибка: файл XML повреждён или имеет неверный формат.")
    except Exception as e:
        print(f"Непредвиденная ошибка: {type(e).__name__}: {e}")