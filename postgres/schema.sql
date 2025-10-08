BEGIN;

-- Enumy
CREATE TYPE status_zlecenia AS ENUM ('nowe','w_toku','wstrzymane','zakończone');
CREATE TYPE status_awarii AS ENUM ('otwarte','w_trakcie','zamknięte');

-- Funkcja aktualizacji updated_at
CREATE OR REPLACE FUNCTION set_updated_at() RETURNS trigger AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- PRACOWNICY
CREATE TABLE pracownicy (
  id_pracownika  BIGSERIAL PRIMARY KEY,
  imie           VARCHAR(100) NOT NULL,
  nazwisko       VARCHAR(100) NOT NULL,
  stanowisko     VARCHAR(100),
  login          VARCHAR(100) UNIQUE NOT NULL,
  haslo_hash     VARCHAR(255) NOT NULL,
  aktywny        BOOLEAN DEFAULT TRUE,
  created_at     TIMESTAMPTZ DEFAULT now(),
  updated_at     TIMESTAMPTZ DEFAULT now()
);

CREATE TRIGGER trg_pracownicy_updated
BEFORE UPDATE ON pracownicy
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ZLECENIA
CREATE TABLE zlecenia (
  id_zlecenia    BIGSERIAL PRIMARY KEY,
  nr_zlecenia    VARCHAR(120) UNIQUE NOT NULL,
  produkt        VARCHAR(200) NOT NULL,
  ilosc_docelowa INTEGER CHECK (ilosc_docelowa >= 0),
  data_start     DATE,
  data_koniec    DATE,
  status         status_zlecenia DEFAULT 'nowe',
  created_at     TIMESTAMPTZ DEFAULT now(),
  updated_at     TIMESTAMPTZ DEFAULT now()
);

CREATE TRIGGER trg_zlecenia_updated
BEFORE UPDATE ON zlecenia
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- MELDUNKI PRODUKCJI
CREATE TABLE meldunki_produkcji (
  id_meldunku    BIGSERIAL PRIMARY KEY,
  id_zlecenia    BIGINT REFERENCES zlecenia(id_zlecenia),
  id_pracownika  BIGINT REFERENCES pracownicy(id_pracownika),
  ilosc_ok       INTEGER DEFAULT 0 CHECK (ilosc_ok >= 0),
  ilosc_nok      INTEGER DEFAULT 0 CHECK (ilosc_nok >= 0),
  czas_pracy_min INTEGER DEFAULT 0,
  data_meldunku  TIMESTAMPTZ DEFAULT now(),
  created_at     TIMESTAMPTZ DEFAULT now(),
  updated_at     TIMESTAMPTZ DEFAULT now()
);

-- EWIDENCJA CZASU PRACY
CREATE TABLE ewidencja_czasu (
  id_rekordu     BIGSERIAL PRIMARY KEY,
  id_pracownika  BIGINT REFERENCES pracownicy(id_pracownika),
  czas_start     TIMESTAMPTZ NOT NULL,
  czas_stop      TIMESTAMPTZ,
  id_zlecenia    BIGINT REFERENCES zlecenia(id_zlecenia),
  created_at     TIMESTAMPTZ DEFAULT now(),
  updated_at     TIMESTAMPTZ DEFAULT now(),
  CONSTRAINT ck_czas_stop_ge_start CHECK (czas_stop IS NULL OR czas_stop >= czas_start)
);

-- ZGŁOSZENIA AWARII
CREATE TABLE zgloszenia_awarii (
  id_awarii      BIGSERIAL PRIMARY KEY,
  id_pracownika  BIGINT REFERENCES pracownicy(id_pracownika),
  id_zlecenia    BIGINT REFERENCES zlecenia(id_zlecenia),
  opis           TEXT NOT NULL,
  zdjecie_url    VARCHAR(500),
  status         status_awarii DEFAULT 'otwarte',
  data_zgloszenia TIMESTAMPTZ DEFAULT now(),
  created_at     TIMESTAMPTZ DEFAULT now(),
  updated_at     TIMESTAMPTZ DEFAULT now()
);

COMMIT;

CREATE TABLE obecnosci (
    id_obecnosci SERIAL PRIMARY KEY,
    id_pracownika INT NOT NULL REFERENCES pracownicy(id_pracownika),
    czas_start TIMESTAMP NOT NULL,
    czas_stop TIMESTAMP
);