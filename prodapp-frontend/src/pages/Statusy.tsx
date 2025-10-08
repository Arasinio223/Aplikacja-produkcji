import { useEffect, useState } from "react";
import api from "../api";

export default function Statusy({ id_pracownika }: { id_pracownika: number }) {
  const [statusy, setStatusy] = useState<string[]>([]);
  const [msg, setMsg] = useState("");

  useEffect(() => {
    api.get("/statusy").then((res) => setStatusy(res.data));
  }, []);

  const zmienStatus = async (status: string) => {
    const res = await api.post("/status/zmiana", null, {
      params: { id_pracownika, status },
    });
    setMsg(res.data.message);
  };

  return (
    <div className="p-4">
      <h1 className="text-xl font-bold mb-3">Zmień status</h1>
      <div className="grid grid-cols-2 gap-3">
        {statusy.map((s) => (
          <button
            key={s}
            onClick={() => zmienStatus(s)}
            className="bg-gray-200 hover:bg-blue-500 hover:text-white rounded p-3 font-semibold"
          >
            {s}
          </button>
        ))}
      </div>
      {msg && <p className="text-green-600 mt-4">{msg}</p>}
    </div>
  );
}
