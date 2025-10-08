import { useEffect, useState } from "react";
import api from "../api";

export default function Zlecenia({ id_pracownika }: { id_pracownika: number }) {
  const [zlecenia, setZlecenia] = useState<any[]>([]);
  const [msg, setMsg] = useState("");

  useEffect(() => {
    api.get("/zlecenia").then((res) => setZlecenia(res.data));
  }, []);

  const wybierz = async (id_zlecenia: number) => {
    const res = await api.post("/wybor_zlecenia", null, {
      params: { id_pracownika, id_zlecenia },
    });
    setMsg(res.data.status);
  };

  return (
    <div className="p-4">
      <h1 className="text-xl font-bold mb-3">Wybierz zlecenie</h1>
      <div className="grid gap-2">
        {zlecenia.map((z) => (
          <button
            key={z.id_zlecenia}
            onClick={() => wybierz(z.id_zlecenia)}
            className="bg-white border shadow rounded-lg p-3 text-left"
          >
            <p className="font-semibold">{z.produkt}</p>
            <p className="text-sm text-gray-500">{z.nr_zlecenia}</p>
          </button>
        ))}
      </div>
      {msg && <p className="text-green-600 mt-4">{msg}</p>}
    </div>
  );
}
