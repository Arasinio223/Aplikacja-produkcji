from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
import models
from database import SessionLocal, engine

# Tworzymy tabele jeśli jeszcze nie istnieją
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="ProdApp API", version="0.2.0")

# --- DB sesja ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Schemat do POST /meldunek
class MeldunekIn(BaseModel):
    id_pracownika: int
    id_zlecenia: int
    ilosc_ok: int
    ilosc_nok: int
    czas_pracy_min: int

@app.get("/")
def home():
    return {"msg": "API działa i jest podłączone do DB ✅"}

@app.post("/meldunek")
def dodaj_meldunek(m: MeldunekIn, db: Session = Depends(get_db)):
    meldunek = models.Meldunek(
        id_pracownika=m.id_pracownika,
        id_zlecenia=m.id_zlecenia,
        ilosc_ok=m.ilosc_ok,
        ilosc_nok=m.ilosc_nok,
        czas_pracy_min=m.czas_pracy_min
    )
    db.add(meldunek)
    db.commit()
    db.refresh(meldunek)
    return {"status": "zapisano", "id_meldunku": meldunek.id_meldunku}

from datetime import datetime
from models import EwidencjaCzasu

# Start pracy
@app.post("/czas/start")
def start_czasu(id_pracownika: int, id_zlecenia: int, db: Session = Depends(get_db)):
    rekord = EwidencjaCzasu(
        id_pracownika=id_pracownika,
        id_zlecenia=id_zlecenia,
        czas_start=datetime.utcnow()
    )
    db.add(rekord)
    db.commit()
    db.refresh(rekord)
    return {"status": "rozpoczęto", "id_rekordu": rekord.id_rekordu}

# Stop pracy
@app.post("/czas/stop")
def stop_czasu(id_rekordu: int, db: Session = Depends(get_db)):
    rekord = db.query(EwidencjaCzasu).filter_by(id_rekordu=id_rekordu).first()
    if not rekord:
        return {"error": "Nie znaleziono rekordu"}
    if rekord.czas_stop:
        return {"error": "Rekord już zakończony"}
    rekord.czas_stop = datetime.utcnow()
    db.commit()
    db.refresh(rekord)
    return {"status": "zakończono", "id_rekordu": rekord.id_rekordu, "czas_stop": rekord.czas_stop}
