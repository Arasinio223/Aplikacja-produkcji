from pydantic import BaseModel
from datetime import date
from pydantic import BaseModel
from datetime import datetime
from models import StatusObecnosciEnum

class ZlecenieSchema(BaseModel):
    id_zlecenia: int
    nr_zlecenia: str
    indeks: str | None = None
    produkt: str
    sztuk: int
    deadline: date | None = None
    kontrakt: str | None = None
    zl_klienta: str | None = None
    liczba_elementow: int | None = None
    waga_szt: float | None = None

    class Config:
        from_attributes = True
        
class ObecnoscBase(BaseModel):
    id_pracownika: int
    status: StatusObecnosciEnum


class ObecnoscCreate(ObecnoscBase):
    pass


class ObecnoscResponse(ObecnoscBase):
    id_obecnosci: int
    czas_start: datetime
    czas_stop: datetime | None

    class Config:
        from_attributes = True