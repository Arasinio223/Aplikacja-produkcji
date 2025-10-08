import { useNavigate } from "react-router-dom";

export default function Dashboard({ id }: { id: number }) {
  const navigate = useNavigate();

  return (
    <div className="p-6 flex flex-col gap-4">
      <h1 className="text-2xl font-bold mb-4">Panel pracownika #{id}</h1>

      <button onClick={() => navigate("/statusy")} className="bg-blue-500 text-white p-3 rounded-lg">
        Statusy / Obecność
      </button>

      <button onClick={() => navigate("/zlecenia")} className="bg-green-500 text-white p-3 rounded-lg">
        Zlecenia produkcyjne
      </button>

      <button onClick={() => navigate("/meldunki")} className="bg-orange-500 text-white p-3 rounded-lg">
        Meldunki
      </button>
    </div>
  );
}
