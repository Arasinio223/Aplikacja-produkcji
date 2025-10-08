import { useEffect, useState } from "react";
import { apiGet } from "../api";

interface Obecnosc {
  id_pracownika: number;
  imie: string;
  nazwisko: string;
  godzina_start: string;
  czas_pracy: string;
  status: string;
  id_zlecenia: number | null;
}

export default function ListaObecnosci() {
  const [obecni, setObecni] = useState<Obecnosc[]>([]);

  useEffect(() => {
    const load = async () => {
      const data = await apiGet("/obecnosc");
      setObecni(data);
    };
    load();
    const timer = setInterval(load, 60_000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="mt-8 w-full max-w-4xl">
      <h2 className="text-xl font-semibold mb-3">Obecni w pracy</h2>
      <table className="min-w-full bg-white rounded-lg shadow-md overflow-hidden">
        <thead className="bg-blue-600 text-white">
          <tr>
            <th className="py-2 px-3 text-left">Pracownik</th>
            <th className="py-2 px-3 text-left">Start</th>
            <th className="py-2 px-3 text-left">Czas pracy</th>
            <th className="py-2 px-3 text-left">Status</th>
            <th className="py-2 px-3 text-left">Zlecenie</th>
          </tr>
        </thead>
        <tbody>
          {obecni.map((p) => (
            <tr key={p.id_pracownika} className="border-b hover:bg-gray-50">
              <td className="py-2 px-3">{p.imie} {p.nazwisko}</td>
              <td className="py-2 px-3">{p.godzina_start}</td>
              <td className="py-2 px-3">{p.czas_pracy}</td>
              <td className="py-2 px-3">{p.status}</td>
              <td className="py-2 px-3">{p.id_zlecenia ?? "-"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
