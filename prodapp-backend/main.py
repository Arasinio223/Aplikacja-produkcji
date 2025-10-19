from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
import re
from fastapi import HTTPException, Query
from typing import Optional
from datetime import datetime, date, timezone
import models
from database import SessionLocal, engine
import models, schemas
from models import Base
from database import engine
from fastapi import File, UploadFile
import pandas as pd
import io
from sqlalchemy.orm import joinedload
from fastapi import APIRouter, Depends
from datetime import datetime
from models import StatusObecnosciEnum
from sqlalchemy import or_
from fastapi.middleware.cors import CORSMiddleware


router = APIRouter()

# to utworzy wszystkie tabele zdefiniowane w models.py
models.Base.metadata.create_all(bind=engine)


app = FastAPI(title="ProdApp API", version="0.3.0")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # na testy, potem możesz zawęzić np. ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class StatusChangeIn(BaseModel):
    id_pracownika: int
    status: StatusObecnosciEnum

# --- DB sesja ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Schematy danych ---
class MeldunekIn(BaseModel):
    id_pracownika: int
    id_zlecenia: int
    ilosc_ok: int
    ilosc_nok: int
    czas_pracy_min: int

class MeldunekCreate(BaseModel):
    id_pracownika: int
    id_zlecenia: int
    ilosc_ok: int
    ilosc_nok: int
    czas_pracy_min: int

class LoginIn(BaseModel):
    login: str
    haslo: str


# --- ENDPOINTY ---
@app.get("/")
def home():
    return {"msg": "API działa i jest podłączone do DB ✅"}


@app.post("/login")
def login(data: LoginIn, db: Session = Depends(get_db)):
    # Walidacja loginu (4 litery)
    if not re.fullmatch(r"[A-Za-z]{4}", data.login):
        return {"error": "Login musi zawierać dokładnie 4 litery"}

    # Walidacja hasła (6 cyfr)
    if not re.fullmatch(r"\d{6}", data.haslo):
        return {"error": "Hasło musi zawierać dokładnie 6 cyfr"}

    # Szukanie użytkownika
    pracownik = db.query(models.Pracownik).filter_by(login=data.login).first()
    if not pracownik:
        return {"error": "Nie znaleziono użytkownika"}

    # (UWAGA: teraz zapisujemy hasło jawnie, ale w przyszłości warto zrobić hash)
    if pracownik.haslo_hash != data.haslo:
        return {"error": "Błędne hasło"}

    return {
        "status": "zalogowano",
        "id_pracownika": pracownik.id_pracownika
    }




@app.get("/pracownicy")
def lista_pracownikow(db: Session = Depends(get_db)):
    pracownicy = db.query(models.Pracownik).all()
    return [
        {
            "id": p.id_pracownika,
            "imie": p.imie,
            "nazwisko": p.nazwisko,
            "login": p.login,
            "aktywny": p.aktywny
        }
        for p in pracownicy
    ]
class PracownikIn(BaseModel):
    imie: str
    nazwisko: str
    login: str
    haslo: str


@app.post("/pracownicy")
def dodaj_pracownika(p: PracownikIn, db: Session = Depends(get_db)):
    # Walidacja loginu (dokładnie 4 litery)
    if not re.fullmatch(r"[A-Za-z]{4}", p.login):
        return {"error": "Login musi zawierać dokładnie 4 litery"}

    # Walidacja hasła (dokładnie 6 cyfr)
    if not re.fullmatch(r"\d{6}", p.haslo):
        return {"error": "Hasło musi zawierać dokładnie 6 cyfr"}

    # Sprawdź, czy login już istnieje
    istnieje = db.query(models.Pracownik).filter_by(login=p.login).first()
    if istnieje:
        return {"error": "Taki login już istnieje"}

    # Dodaj pracownika
    nowy = models.Pracownik(
        imie=p.imie,
        nazwisko=p.nazwisko,
        login=p.login,
        haslo_hash=p.haslo,  # UWAGA: tu hasło jest jawne, w produkcji trzeba będzie zahashować
        aktywny=True
    )
    db.add(nowy)
    db.commit()
    db.refresh(nowy)

    return {
        "status": "dodano",
        "id_pracownika": nowy.id_pracownika,
        "login": nowy.login
    }

@app.post("/zlecenia/import")
def import_zlecen_excel(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".xlsx"):
        return {"error": "Tylko pliki Excel (.xlsx) są obsługiwane"}

    # Wczytaj dane z pliku Excel
    contents = file.file.read()
    df = pd.read_excel(io.BytesIO(contents))

    # Wymagane kolumny
    required_cols = {"nr_zlecenia", "Indeks", "produkt", "sztuk", "deadline", 
                     "kontrakt", "zl_klienta", "liczba_elementów", "waga_szt"}
    if not required_cols.issubset(df.columns):
        return {"error": f"Plik musi zawierać kolumny: {required_cols}"}

    dodane = 0
    pominiete = 0

    for _, row in df.iterrows():
        if not row["nr_zlecenia"] or not row["produkt"]:
            pominiete += 1
            continue

        # Sprawdź, czy zlecenie już istnieje
        istnieje = db.query(models.Zlecenie).filter_by(nr_zlecenia=str(row["nr_zlecenia"])).first()
        if istnieje:
            pominiete += 1
            continue

        # Konwersja deadline (może być w formacie daty Excela albo string dd.mm.yyyy)
        if isinstance(row["deadline"], str):
            deadline = datetime.strptime(row["deadline"], "%d.%m.%Y")
        else:
            deadline = pd.to_datetime(row["deadline"]).to_pydatetime()

        # Utwórz obiekt
        zlecenie = models.Zlecenie(
            nr_zlecenia=str(row["nr_zlecenia"]),
            indeks=str(row["Indeks"]),
            produkt=str(row["produkt"]),
            sztuk=int(row["sztuk"]),
            deadline=deadline,
            kontrakt=str(row["kontrakt"]),
            zl_klienta=str(row["zl_klienta"]),
            liczba_elementow=int(row["liczba_elementów"]),
            waga_szt=int(row["waga_szt"])
        )
        db.add(zlecenie)
        dodane += 1

    db.commit()
    return {"status": "ok", "dodane": dodane, "pominiete": pominiete}

#@app.get("/zlecenia")
#def lista_zlecen(db: Session = Depends(get_db)):
 #   zlecenia = db.query(models.Zlecenie).all()
  #  return [
   #     {
    #        "id": z.id_zlecenia,
     #       "nr_zlecenia": z.nr_zlecenia,
      #      "produkt": z.produkt
       # }
        #for z in zlecenia
    #]

@app.get("/zlecenia", response_model=list[schemas.ZlecenieSchema])
def lista_zlecen(db: Session = Depends(get_db)):
    return db.query(models.Zlecenie).all()

@app.delete("/zlecenia/{zlecenie_id}")
def usun_zlecenie(zlecenie_id: int, db: Session = Depends(get_db)):
    zlecenie = db.query(models.Zlecenie).filter_by(id_zlecenia=zlecenie_id).first()
    if not zlecenie:
        return {"error": "Nie znaleziono zlecenia"}

    db.delete(zlecenie)
    db.commit()
    return {"status": "usunięto", "id": zlecenie_id}



@app.post("/obecnosc/start")
def start_obecnosci(id_pracownika: int, db: Session = Depends(get_db)):
    # Sprawdź, czy pracownik już jest "zalogowany"
    aktywna = db.query(models.Obecnosc).filter(
        models.Obecnosc.id_pracownika == id_pracownika,
        models.Obecnosc.czas_stop == None
    ).first()

    if aktywna:
        return {"error": "Pracownik już rozpoczął obecność i nie zakończył"}

    nowa = models.Obecnosc(
        id_pracownika=id_pracownika,
        czas_start=datetime.utcnow()
    )
    db.add(nowa)
    db.commit()
    db.refresh(nowa)
    return {"status": "obecność rozpoczęta", "id_obecnosci": nowa.id_obecnosci}

@app.post("/obecnosc/stop")
def stop_obecnosci(id_pracownika: int, db: Session = Depends(get_db)):
    aktywna = db.query(models.Obecnosc).filter(
        models.Obecnosc.id_pracownika == id_pracownika,
        models.Obecnosc.czas_stop == None
    ).first()

    if not aktywna:
        return {"error": "Brak aktywnej obecności do zakończenia"}

    aktywna.czas_stop = datetime.utcnow()
    db.commit()
    db.refresh(aktywna)

    return {
        "status": "obecność zakończona",
        "id_obecnosci": aktywna.id_obecnosci,
        "czas_stop": aktywna.czas_stop
    }





@app.get("/obecnosc")
def lista_obecnosci(id_pracownika: int = None, db: Session = Depends(get_db)):
    teraz = datetime.now(timezone.utc)

    query = (
        db.query(models.Obecnosc, models.Pracownik)
        .join(models.Pracownik, models.Obecnosc.id_pracownika == models.Pracownik.id_pracownika)
        .filter(models.Obecnosc.czas_stop == None)
    )

    if id_pracownika:
        query = query.filter(models.Obecnosc.id_pracownika == id_pracownika)

    obecni = query.all()
    wynik = []
    for obecnosc, pracownik in obecni:
        czas_start = obecnosc.czas_start
        godzina_start = czas_start.strftime("%H:%M")
        roznica = teraz - czas_start
        godziny = roznica.total_seconds() // 3600
        minuty = (roznica.total_seconds() % 3600) // 60

        wynik.append({
            "id_pracownika": pracownik.id_pracownika,
            "imie": pracownik.imie,
            "nazwisko": pracownik.nazwisko,
            "godzina_start": godzina_start,
            "czas_pracy": f"{int(godziny)}h {int(minuty)}m",
            "status": obecnosc.status,
            "id_zlecenia": obecnosc.id_zlecenia  # Dodaj to pole
        })

    return wynik

@app.post("/meldunek/stop")
def stop_meldunku(id_pracownika: int, ilosc_ok: int, ilosc_nok: int, db: Session = Depends(get_db)):
    aktywny = db.query(models.Meldunek).filter(
        models.Meldunek.id_pracownika == id_pracownika,
        models.Meldunek.czas_stop == None
    ).first()

    if not aktywny:
        return {"error": "Brak aktywnego meldunku"}

    aktywny.czas_stop = datetime.utcnow()
    aktywny.ilosc_ok = ilosc_ok
    aktywny.ilosc_nok = ilosc_nok

    # policz czas w minutach
    diff = aktywny.czas_stop - aktywny.czas_start
    aktywny.czas_pracy_min = int(diff.total_seconds() // 60)

    db.commit()
    db.refresh(aktywny)

    return {
        "status": "meldunek zakończony",
        "id_meldunku": aktywny.id_meldunku,
        "czas_pracy_min": aktywny.czas_pracy_min,
        "ilosc_ok": aktywny.ilosc_ok,
        "ilosc_nok": aktywny.ilosc_nok
    }
# =======================
# STATUSY OBECNOŚCI
# =======================

@app.post("/status/zmiana")
def zmiana_statusu(payload: StatusChangeIn, db: Session = Depends(get_db)):
    id_pracownika = payload.id_pracownika
    status = payload.status
    # Zamknij poprzedni status
    ostatni_status = (
        db.query(models.Obecnosc)
        .filter(models.Obecnosc.id_pracownika == id_pracownika, models.Obecnosc.czas_stop == None)
        .first()
    )
    if ostatni_status:
        ostatni_status.czas_stop = datetime.utcnow()
        db.commit()

    # Jeśli nowy status to praca_normalna, znajdź ostatnie zlecenie
    ostatnie_zlecenie = db.query(models.Obecnosc).filter(
        models.Obecnosc.id_pracownika == id_pracownika,
        models.Obecnosc.id_zlecenia != None
    ).order_by(models.Obecnosc.czas_start.desc()).first()

    if status == StatusObecnosciEnum.PRACA_NORMALNA and ostatnie_zlecenie:
        nowy_status = models.Obecnosc(
            id_pracownika=id_pracownika,
            czas_start=datetime.utcnow(),
            status=status,
            id_zlecenia=ostatnie_zlecenie.id_zlecenia
        )
    else:
        nowy_status = models.Obecnosc(
            id_pracownika=id_pracownika,
            czas_start=datetime.utcnow(),
            status=status
        )
    db.add(nowy_status)
    db.commit()
    db.refresh(nowy_status)

    return {"message": f"Zmiana Statusu na {status.value}"}


@app.get("/statusy")
def lista_statusow():
    return [s.value for s in StatusObecnosciEnum]

@app.get("/zlecenia/search", response_model=list[schemas.ZlecenieSchema])
def search_zlecenia(q: str, db: Session = Depends(get_db)):
    # Szukaj po kilku polach tekstowych
    zlecenia = db.query(models.Zlecenie).filter(
        or_(
            models.Zlecenie.nr_zlecenia.ilike(f"%{q}%"),
            models.Zlecenie.indeks.ilike(f"%{q}%"),
            models.Zlecenie.produkt.ilike(f"%{q}%"),
            models.Zlecenie.kontrakt.ilike(f"%{q}%"),
            models.Zlecenie.zl_klienta.ilike(f"%{q}%")
        )
    ).all()
    return zlecenia

@app.get("/historia/{id_pracownika}")
def historia_pracownika(id_pracownika: int, db: Session = Depends(get_db)):
    # Historia statusów obecności
    obecnosci = db.query(models.Obecnosc).filter(
        models.Obecnosc.id_pracownika == id_pracownika
    ).order_by(models.Obecnosc.czas_start.desc()).all()

    obecnosci_historia = [
        {
            "typ": "obecnosc",
            "czas_start": o.czas_start,
            "czas_stop": o.czas_stop,
            "status": o.status,
            "id_zlecenia": o.id_zlecenia
        }
        for o in obecnosci
    ]

    # Historia meldunków
    meldunki = db.query(models.Meldunek).filter(
        models.Meldunek.id_pracownika == id_pracownika
    ).order_by(models.Meldunek.czas_start.desc()).all()

    meldunki_historia = [
        {
            "typ": "meldunek",
            "czas_start": m.czas_start,
            "czas_stop": m.czas_stop,
            "id_zlecenia": m.id_zlecenia
        }
        for m in meldunki
    ]

    # Połącz historię i posortuj po czasie start
    historia = obecnosci_historia + meldunki_historia
    historia.sort(key=lambda x: x["czas_start"], reverse=True)

    return historia

@app.post("/wybor_zlecenia")
def wybor_zlecenia(id_pracownika: int, id_zlecenia: int, db: Session = Depends(get_db)):
    """
    Pracownik wybiera zlecenie produkcyjne.
    Zapisz id_zlecenia jako informację dodatkową w obecności i ustaw status na praca_normalna.
    """
    # Znajdź aktywną obecność pracownika
    obecnosc = db.query(models.Obecnosc).filter(
        models.Obecnosc.id_pracownika == id_pracownika,
        models.Obecnosc.czas_stop == None
    ).first()
    if not obecnosc:
        return {"error": "Pracownik nie jest obecny w pracy"}

    # Zapisz wybrane zlecenie jako informację dodatkową
    obecnosc.id_zlecenia = id_zlecenia  # Dodaj pole id_zlecenia do modelu Obecnosc jeśli nie istnieje
    obecnosc.status = StatusObecnosciEnum.PRACA_NORMALNA
    db.commit()
    db.refresh(obecnosc)

    return {
        "status": "praca_normalna",
        "id_pracownika": id_pracownika,
        "id_zlecenia": id_zlecenia
    }