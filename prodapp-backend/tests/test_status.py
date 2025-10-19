import sys
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base
from main import app, get_db
import models
from datetime import datetime
from sqlalchemy import TypeDecorator, DateTime
import pytz

# Custom TypeDecorator to handle timezone-aware datetimes in SQLite
class TZDateTime(TypeDecorator):
    impl = DateTime
    LOCAL_TIMEZONE = pytz.utc
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            return value.astimezone(self.LOCAL_TIMEZONE)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return value.replace(tzinfo=self.LOCAL_TIMEZONE)
        return value

models.Obecnosc.__table__.c.czas_start.type = TZDateTime()
models.Obecnosc.__table__.c.czas_stop.type = TZDateTime()


SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


client = TestClient(app)

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

def test_zmien_status_rozpoczecie_pracy(db_session):
    # Dodaj pracownika
    pracownik = models.Pracownik(imie="Jan", nazwisko="Kowalski", login="test", haslo_hash="123456")
    db_session.add(pracownik)
    db_session.commit()

    # Zmień status na "szatnia"
    response = client.post("/pracownicy/zmien-status", json={"id_pracownika": pracownik.id_pracownika, "status": "szatnia"})
    assert response.status_code == 200
    assert response.json()["message"] == "Zmieniono status na: szatnia"

    # Sprawdź, czy status został zapisany w bazie
    obecnosc = db_session.query(models.Obecnosc).filter_by(id_pracownika=pracownik.id_pracownika).first()
    assert obecnosc is not None
    assert obecnosc.status == models.StatusObecnosciEnum.SZATNIA
    assert obecnosc.czas_stop is None

def test_zmien_status_zakonczenie_pracy(db_session):
    # Dodaj pracownika i rozpocznij pracę
    pracownik = models.Pracownik(imie="Jan", nazwisko="Kowalski", login="test", haslo_hash="123456")
    db_session.add(pracownik)
    db_session.commit()
    client.post("/pracownicy/zmien-status", json={"id_pracownika": pracownik.id_pracownika, "status": "praca"})

    # Zakończ pracę
    response = client.post("/pracownicy/zmien-status", json={"id_pracownika": pracownik.id_pracownika, "status": "wyjscie_z_pracy"})
    assert response.status_code == 200
    assert response.json()["message"] == "Zakończono dzień pracy."

    # Sprawdź, czy status został zamknięty
    obecnosc = db_session.query(models.Obecnosc).filter_by(id_pracownika=pracownik.id_pracownika).first()
    assert obecnosc is not None
    assert obecnosc.czas_stop is not None

def test_wybor_zlecenia_poprawny_status(db_session):
    # Dodaj pracownika, zlecenie i rozpocznij pracę
    pracownik = models.Pracownik(imie="Jan", nazwisko="Kowalski", login="test", haslo_hash="123456")
    zlecenie = models.Zlecenie(nr_zlecenia="123", indeks="indeks-test", produkt="Test", sztuk=10, deadline=datetime.now())
    db_session.add(pracownik)
    db_session.add(zlecenie)
    db_session.commit()
    client.post("/pracownicy/zmien-status", json={"id_pracownika": pracownik.id_pracownika, "status": "praca"})

    # Wybierz zlecenie
    response = client.post("/wybor_zlecenia", params={"id_pracownika": pracownik.id_pracownika, "id_zlecenia": zlecenie.id_zlecenia})
    assert response.status_code == 200
    assert response.json()["message"] == "Przypisano zlecenie do pracownika"

    # Sprawdź, czy zlecenie zostało przypisane
    obecnosc = db_session.query(models.Obecnosc).filter_by(id_pracownika=pracownik.id_pracownika).first()
    assert obecnosc.id_zlecenia == zlecenie.id_zlecenia

def test_wybor_zlecenia_niepoprawny_status(db_session):
    # Dodaj pracownika, zlecenie i zmień status na "przerwa"
    pracownik = models.Pracownik(imie="Jan", nazwisko="Kowalski", login="test", haslo_hash="123456")
    zlecenie = models.Zlecenie(nr_zlecenia="123", indeks="indeks-test", produkt="Test", sztuk=10, deadline=datetime.now())
    db_session.add(pracownik)
    db_session.add(zlecenie)
    db_session.commit()
    client.post("/pracownicy/zmien-status", json={"id_pracownika": pracownik.id_pracownika, "status": "przerwa"})

    # Spróbuj wybrać zlecenie
    response = client.post("/wybor_zlecenia", params={"id_pracownika": pracownik.id_pracownika, "id_zlecenia": zlecenie.id_zlecenia})
    assert response.status_code == 400
    assert response.json()["detail"] == "Nie można wybrać zlecenia. Pracownik nie jest w trybie 'praca'."

def test_moj_status(db_session):
    # Dodaj pracownika i rozpocznij pracę
    pracownik = models.Pracownik(imie="Jan", nazwisko="Kowalski", login="test", haslo_hash="123456")
    db_session.add(pracownik)
    db_session.commit()
    client.post("/pracownicy/zmien-status", json={"id_pracownika": pracownik.id_pracownika, "status": "praca"})

    # Pobierz status
    response = client.get(f"/pracownicy/{pracownik.id_pracownika}/moj-status")
    assert response.status_code == 200
    data = response.json()
    assert data["imie"] == "Jan"
    assert data["nazwisko"] == "Kowalski"
    assert data["status"] == "praca"
    assert "h" in data["czas_trwania"] and "m" in data["czas_trwania"]
