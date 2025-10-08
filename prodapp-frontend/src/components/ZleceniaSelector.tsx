import { useEffect, useState } from "react";
import { apiGet, apiPost } from "../api";

interface Props {
  idPracownika: number;
}

interface Zlecenie {
  id_zlecenia: number;
  nr_zlecenia: string;
  produkt: string;
}

export default function ZleceniaSelector({ idPracownika }: Props) {
  const [zlecenia, setZlecenia] = useState<Zlecenie[]>([]);
  const [selected, setSelected] = useState<number | null>(null);
  const [msg, setMsg] = useState("");

  useEffect(() => {
    apiGet("/zlecenia").then(setZlecenia).catch(console.error);
  }, []);

  const wybierzZlecenie = async (id_zlecenia: number) => {
    try {
      const res = await apiPost("/wybor_zlecenia", {
        id_pracownika: idPracownika,
        id_zlecenia,
      });
      setSelected(id_zlecenia);
      setMsg(`Zalogowano na zlecenie ${res.id_zlecenia}`);
    } catch {
      setMsg("Błąd podczas wyboru zlecenia");
    }
  };

  return (
    <div className="bg-white p-6 rounded-xl shadow-md w-full max-w-md mt-6">
      <h2 className="text-xl font-semibold mb-4">Wybierz zlecenie</h2>
      <div className="flex flex-col gap-2 max-h-60 overflow-y-auto">
        {zlecenia.map((z) => (
          <button
            key={z.id_zlecenia}
            onClick={() => wybierzZlecenie(z.id_zlecenia)}
            className={`border rounded px-3 py-2 text-left ${
              selected === z.id_zlecenia
                ? "bg-green-100 border-green-500"
                : "hover:bg-gray-100"
            }`}
          >
            <strong>{z.nr_zlecenia}</strong> — {z.produkt}
          </button>
        ))}
      </div>
      {msg && <p className="text-center text-gray-600 mt-4">{msg}</p>}
    </div>
  );
}
