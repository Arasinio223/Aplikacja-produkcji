BEGIN;

INSERT INTO pracownicy (imie, nazwisko, stanowisko, login, haslo_hash)
VALUES
('Anna','Kowalska','operator','anna.k','HASHED_PASSWORD'),
('Piotr','Nowak','lider','piotr.n','HASHED_PASSWORD');

INSERT INTO zlecenia (nr_zlecenia, produkt, ilosc_docelowa, data_start, data_koniec, status)
VALUES
('ZL-2025-0001','Obudowa A12', 500, CURRENT_DATE, CURRENT_DATE + INTERVAL '5 day', 'w_toku');

COMMIT;
