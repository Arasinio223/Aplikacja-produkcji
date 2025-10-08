import { useEffect, useState } from "react";
import { apiGet, apiPost } from "../api";

interface Props {
  idPracownika: number;
}

export default function StatusSelector({ idPracownika }: Props) {
  const [statusy, setStatusy] = useState<string[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [message, setMessage] = useState("");

  useEffect(() => {
    apiGet("/statusy").then(setStatusy).catch(console.error);
  }, []);

  const handleStatusChange = async (status: string) => {
    try {
      const res = await apiPost("/status/zmiana", {
        id_pracownika: idPracownika,
        status,
      });
      setSelected(status);
      setMessage(res.message);
    } catch {
      setMessage("Błąd zmiany statusu");
    }
  };

  return (
    <div className="bg-white p-6 rounded-xl shadow-md w-full max-w-md">
      <h2 className="text-xl font-semibold mb-4">Status obecności</h2>
      <div className="grid grid-cols-2 gap-3">
        {statusy.map((s) => (
          <button
            key={s}
            onClick={() => handleStatusChange(s)}
            className={`py-2 px-4 rounded text-white ${
              selected === s ? "bg-green-600" : "bg-blue-500 hover:bg-blue-600"
            }`}
          >
            {s.replace("_", " ")}
          </button>
        ))}
      </div>
      {message && <p className="text-gray-600 mt-4 text-center">{message}</p>}
    </div>
  );
}
