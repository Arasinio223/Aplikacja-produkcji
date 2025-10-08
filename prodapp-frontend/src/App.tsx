import { useState, useEffect } from "react";
import Login from "./components/Login";
import StatusSelector from "./components/StatusSelector";
import ZleceniaSelector from "./components/ZleceniaSelector";
import ListaObecnosci from "./components/ListaObecnosci";

export default function App() {
  const [idPracownika, setIdPracownika] = useState<number | null>(null);

  if (!idPracownika) {
    return <Login onLogin={setIdPracownika} />;
  }

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center p-6">
      <h1 className="text-3xl font-bold text-blue-700 mb-6">Panel pracownika</h1>
      <StatusSelector idPracownika={idPracownika} />
      <ZleceniaSelector idPracownika={idPracownika} />
      <ListaObecnosci />
    </div>
  );
}