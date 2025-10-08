import { useState } from "react";
import api from "../api";

export default function Meldunki({ id_pracownika }: { id_pracownika: number }) {
  const [iloscOK, setIloscOK] = useState(0);
  const [iloscNOK, setIloscNOK] = useState(0);
  const [msg, setMsg] = useState("");

  const stopMeldunek = async () => {
    const res = await api.post("/meldunek/stop", null, {
      params: { id_pracownika, ilosc_ok: iloscOK, ilosc_nok: iloscNOK },
    });
    setMsg(res.data.status);
  };

  return (
    <div className="p-4">
      <h1 className="text-xl font-bold mb-3">Zakończ meldunek</h1>
      <div className="flex flex-col gap-2">
        <input
          type="number"
          placeholder="Ilość OK"
          value={iloscOK}
          onChange={(e) => setIloscOK(parseInt(e.target.value))}
          className="border rounded p-2"
        />
        <input
          type="number"
          placeholder="Ilość NOK"
          value={iloscNOK}
          onChange={(e) => setIloscNOK(parseInt(e.target.value))}
          className="border rounded p-2"
        />
        <button onClick={stopMeldunek} className="bg-blue-600 text-white p-3 rounded-lg">
          Zakończ meldunek
        </button>
        {msg && <p className="text-green-600 mt-2">{msg}</p>}
      </div>
    </div>
  );
}
