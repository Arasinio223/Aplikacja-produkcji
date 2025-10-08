from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
from sqlalchemy import ForeignKey
import enum
from sqlalchemy import Enum

Base = declarative_base()

class Pracownik(Base):
    __tablename__ = "pracownicy"
    id_pracownika = Column(Integer, primary_key=True, index=True)
    imie = Column(String, nullable=False)
    nazwisko = Column(String, nullable=False)
    login = Column(String, unique=True, nullable=False)
    haslo_hash = Column(String, nullable=False)
    aktywny = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    obecnosci = relationship("Obecnosc", back_populates="pracownik")
    meldunki = relationship("Meldunek", back_populates="pracownik")

class Zlecenie(Base):
    __tablename__ = "zlecenia"

    id_zlecenia = Column(Integer, primary_key=True, index=True)
    nr_zlecenia = Column(String(50), unique=True, nullable=False)
    indeks = Column(String(50), nullable=False)
    produkt = Column(String, nullable=False)
    sztuk = Column(Integer, nullable=False)
    deadline = Column(DateTime, nullable=False)
    kontrakt = Column(String(50), nullable=True)
    zl_klienta = Column(String(50), nullable=True)
    liczba_elementow = Column(Integer, nullable=True)
    waga_szt = Column(Integer, nullable=True)
    meldunki = relationship("Meldunek", back_populates="zlecenie")

class StatusObecnosciEnum(str, enum.Enum):
    PRACA_NORMALNA = "praca_normalna"
    SZATNIA = "szatnia"
    PALARNIA = "palarnia"
    WYJSCIE_SLUZBOWE = "wyjscie_sluzbowe"
    WYJSCIE_PRYWATNE = "wyjscie_prywatne"
    PRZERWA = "przerwa"
    PRZERWA_PAPIEROS = "przerwa_papieros"
    AWARIA = "awaria"
    PRACA_ZDALNA = "praca_zdalna"
    SZKOLENIE = "szkolenie"
    OCZEKIWANIE_MATERIALY = "oczekiwanie_materialy"

class Obecnosc(Base):
    __tablename__ = "obecnosci"
    id_obecnosci = Column(Integer, primary_key=True, autoincrement=True)
    id_pracownika = Column(Integer, ForeignKey("pracownicy.id_pracownika"), nullable=False)
    czas_start = Column(DateTime(timezone=True), server_default=func.now())
    czas_stop = Column(DateTime(timezone=True), nullable=True)
    status = Column(Enum(StatusObecnosciEnum), nullable=False, default=StatusObecnosciEnum.PRACA_NORMALNA)
    id_zlecenia = Column(Integer, ForeignKey("zlecenia.id_zlecenia"), nullable=True)  # Dodaj to pole

    pracownik = relationship("Pracownik", back_populates="obecnosci")


# ======================
# MELDUNKI PRODUKCJI
# ======================
class Meldunek(Base):
    __tablename__ = "meldunki_produkcji"

    id_meldunku = Column(Integer, primary_key=True, index=True)
    id_zlecenia = Column(Integer, ForeignKey("zlecenia.id_zlecenia"))
    id_pracownika = Column(Integer, ForeignKey("pracownicy.id_pracownika"))
    ilosc_ok = Column(Integer, default=0)
    ilosc_nok = Column(Integer, default=0)
    czas_start = Column(DateTime(timezone=True), server_default=func.now())
    czas_stop = Column(DateTime(timezone=True), nullable=True)

    zlecenie = relationship("Zlecenie", back_populates="meldunki")
    pracownik = relationship("Pracownik", back_populates="meldunki")


# ======================
# EWIDENCJA CZASU (opcjonalnie)
# ======================
class EwidencjaCzasu(Base):
    __tablename__ = "ewidencja_czasu"

    id_rekordu = Column(Integer, primary_key=True, index=True)
    id_pracownika = Column(Integer, ForeignKey("pracownicy.id_pracownika"))
    id_zlecenia = Column(Integer, ForeignKey("zlecenia.id_zlecenia"))
    czas_start = Column(DateTime(timezone=True), server_default=func.now())
    czas_stop = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())



