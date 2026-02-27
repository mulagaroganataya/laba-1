from datetime import datetime
import uuid

from exceptions import ValidationError


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex}"


def dt_to_str(dt: datetime) -> str:
    return dt.isoformat(timespec="seconds")


def str_to_dt(s: str) -> datetime:
    return datetime.fromisoformat(s)


def ensure_nonempty(value: str, field_name: str) -> None:
    if not value or not value.strip():
        raise ValidationError(f"Поле '{field_name}' не должно быть пустым.")